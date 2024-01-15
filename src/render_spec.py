"""
* Render Spec Module
* Handles parsing render spec file, aka text files that contain a set of configurations and cards to render
"""
# Standard Library Imports
import os
import glob
import re as regex
from pathlib import Path
from typing import Dict, TypedDict, Optional, Any

# Local Imports
from src.cards import CardDetails, parse_card_info

"""
* Types
"""

class RenderConfiguration(TypedDict):
    name: str
    info: str

class RenderSpec(TypedDict):
    """Render spec obtained from parsing the file."""
    name: str
    file: Path
    configs: Dict[str, RenderConfiguration]
    cards: list[CardDetails]


"""
* File parsing
"""

def parse_render_spec(file_path: Path) -> RenderSpec:
    """Retrieve render spec from the input file.

    Args:
        file_path: Path to the text file.

    Returns:
        Dict containing the configurations and cards in this spec.
    """

    # Extract just the spec name
    file_name = file_path.stem
    parent_dir = str(file_path.parent)

    # Load all the content and get rid of empty lines and comments
    spec_lines = open(file_path, 'r').read().splitlines()
    spec_lines = [l.split('#')[0].strip() for l in spec_lines]
    spec_lines = [l for l in spec_lines if l]

    # Split lines with configs and lines with cards
    config_lines = [l for l in spec_lines if regex.match(r'([a-zA-Z0-9_ ]+):(.*)', l)]
    card_lines = [l for l in spec_lines if l not in config_lines]

    # Find all the configurations first
    configs = {}
    for l in config_lines:
        [config_name, config_info] = map(str.strip, l.split(':'))
        configs[config_name] = {
            'name': config_name,
            'info': config_info,
        }

    # Now find all the cards and parse them by using the configs
    cards = []
    groups = []
    for l in card_lines:
        # Entering a group
        if l.startswith('{'):
            groups.append([])
            l = l[1:].strip()
            if not l:
                continue

        parts = list(map(str.strip, l.split('|')))
        spec_base = parts[0]

        def append_config(card, config):
            return (card[0] + f' {config}', card[1])

        def append_card(card_spec):
            spec, path = card_spec
            # Pretend this is a file right next to the spec and parse that
            full_card_path = file_path.parent / Path(spec).name
            card_info = parse_card_info(full_card_path)
            if path is not None:
                card_info['additional_cfg']['art'] = path
            cards.append(card_info)

        if '*' in spec_base:
            specs = glob.glob(spec_base, root_dir=parent_dir, recursive=True)
            specs = [(s.split('.')[0], s) for s in specs if not s.endswith('.txt')]
        elif os.path.exists(spec_base):
            specs = [(spec_base.split('.')[0], spec_base)]
        else:
            specs = [(spec_base, None)]

        used_configs = parts[1:]
        for c in used_configs:
            if c in configs:
                config_spec = configs[c]['info']
            else:
                config_spec = c
            specs = [append_config(s, config_spec) for s in specs]
        
        # If part of a group we need to just accumulate
        if groups:
            if l.startswith('}'):
                # The group ended, so we assign this configuration to all the cards in it
                group_spec = specs[0][0][1:].strip()
                ended_group = groups.pop()
                ended_group = [append_config(c, group_spec) for c in ended_group]

                if groups:
                    # Replace special variables
                    ended_group = [c.replace('${GROUP_INDEX}', str(i)) for (i, c) in enumerate(ended_group)]
                    ended_group = [c.replace('${INNER_GROUP_INDEX}', str(i)) for (i, c) in enumerate(ended_group)]
                
                    # If this was a nested group we just put these into the outer group
                    groups[-1].extend(ended_group)
                else:
                    # Replace special variables
                    ended_group = [c.replace('${GROUP_INDEX}', str(i)) for (i, c) in enumerate(ended_group)]
                    ended_group = [c.replace('${OUTER_GROUP_INDEX}', str(i)) for (i, c) in enumerate(ended_group)]

                    # Otherwise append to the render spec
                    for card in ended_group:
                        append_card(card)
            else:
                # Append the card to the group
                groups[-1].extend(specs)
        else:
            for card_spec in specs: 
                append_card(card_spec)

    # Return dictionary
    return {
        'name': file_name,
        'file': file_path,
        'configs': configs,
        'cards': cards,
    }
