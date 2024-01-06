"""
* Render Spec Module
* Handles parsing render spec file, aka text files that contain a set of configurations and cards to render
"""
# Standard Library Imports
import os
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

def parse_render_spec(file_path: Path, logger: Optional[Any] = None) -> RenderSpec:
    """Retrieve render spec from the input file.

    Args:
        file_path: Path to the text file.
        logger: Console or other logger object used to relay warning messages.

    Returns:
        Dict containing the configurations and cards in this spec.
    """

    # Extract just the spec name
    file_name = file_path.stem

    # Load all the content and get rid of empty lines and comments
    spec_lines = open(file_path, 'r').read().splitlines()
    spec_lines = [l for l in spec_lines if l.split('#')[0].strip()]

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
    for l in card_lines:
        parts = list(map(str.strip, l.split('|')))
        full_card_spec = parts[0]
        used_configs = parts[1:]
        invalid_configs = [c for c in used_configs if c not in configs]
        if invalid_configs:
            if logger:
                logger.update(f'Card ignored due to unknown render spec configurations: {full_card_spec.split()[0]}')
                for c in invalid_configs:
                    logger.update(f'\nUnknown render spec configuration: {c}')
            continue
        for c in used_configs:
            spec_info = configs[c]['info']
            full_card_spec += f' {spec_info}'

        # Pretend this is a file and parse that
        full_card_path = file_path.with_stem(full_card_spec)
        cards.append(parse_card_info(full_card_path))

    # Return dictionary
    return {
        'name': file_name,
        'file': file_path,
        'configs': configs,
        'cards': cards,
    }
