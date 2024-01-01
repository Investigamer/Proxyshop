"""
* CLI Commands: Rendering
"""
# Standard Library Imports
from pathlib import Path

# Third Party Imports
import click

# Local Imports
from src import CON
from src.cards import CardDetails
from src.layouts import layout_map
from src.utils.files import load_data_file

"""
* Commands: Render
* Add a render command
* This is merely an example, will be replaced in the future.
"""


@click.group()
def render_cli():
    """App render CLI."""
    pass


@render_cli.command()
@click.argument('data_file', required=True)
def render_card(data_file: str = None):
    """Render a single card using JSON data."""

    # Load card data from a json file
    data_file = Path(CON.cwd, 'customs', data_file).with_suffix('.json')
    card = load_data_file(data_file)

    # Find your art image file
    art_path = Path(CON.cwd, 'art', data_file)
    for suf in ['.jpg', '.png', '.webp']:
        art_file = art_path.with_suffix(suf)
        if art_file.is_file():
            break

    # Check if proper art file was found
    if not art_file.is_file():
        raise OSError(f"No art file matching name '{data_file}' was found!")

    # Get appropriate layout class
    layout = layout_map.get(card.get('layout', 'normal'))

    # Create a fake file details dict
    file_details: CardDetails = {
        'file': art_file, 'name': card.get('name', ''),
        'set': '', 'artist': '', 'creator': '', 'number': ''
    }

    # Create layout object
    layout(card, file_details)

    # Just grabbing the first template (Normal) from whatever template type the card is
    # You could add your own logic to select the template you want from the list
    # template = get_templates().get(layout.card_class)[0]

    # Add PSD file path to the card layout.
    # layout.template_file = template['template_path']

    # Load the template class, create an instance, execute it
    # get_template_class(template)(layout).execute()


# Export CLI
__all__ = ['render_cli']
