"""
INITIATE AND PREPARE RENDER JOB
"""
import os
import re
from proxyshop import layouts
import proxyshop.constants as con
import proxyshop.scryfall as scry
from plugins import loader

def retrieve_card_info (filename):
    """
    Retrieve card name and (if specified) artist from the input file.
    """
    # Extract just the cardname
    sep = [' {', ' [', ' (']
    fn_split = re.split('|'.join(map(re.escape, sep)), filename[:-4])
    name = fn_split[0]

    # Look for creator, artist, set
    creator = re.findall(r'\{+(.*?)\}', filename)
    artist = re.findall(r'\(+(.*?)\)', filename)
    set_code = re.findall(r'\[+(.*?)\]', filename)

    # Check for these values
    if creator: creator = creator[0]
    else: creator = None
    if artist: artist = artist[0]
    else: artist = None
    if set_code: set_code = set_code[0]
    else: set_code = None

    return {
        'name': name,
        'artist': artist,
        'set': set_code,
        'creator': creator
    }


def render (file,template):
    """
    Set up this render job, then execute
    """
    # pylint: disable=R0912, R1722
    # TODO: specify the desired template for a card in the filename?
    card = retrieve_card_info(os.path.basename(str(file)))

    # Basic land?
    if card['name'] in con.basic_land_names:

        # Manually call the BasicLand layout OBJ
        layout = layouts.BasicLand(card['name'], card['artist'], card['set'].upper())

    else:

        # Get the scryfall info
        scryfall = scry.card_info(card['name'], card['set'])

        # Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
        try: layout = layouts.layout_map[scryfall['layout']](scryfall, card['name'])
        except:
            input(f"Layout '{scryfall['layout']}'' is not supported. Press enter to exit...")
            exit()

        # If artist specified in file name, replace artist in layout OBJ
        if card['artist']: layout.artist = card['artist']

        # Get full set info from scryfall
        mtgset = scry.set_info(layout.set)
        if 'printed_size' in mtgset: layout.card_count = mtgset['printed_size']
        elif 'card_count' in mtgset: layout.card_count = mtgset['card_count']
        else: layout.card_count = "XXX"

    # Get our template and layout class maps
    if isinstance(template, dict):
        card_template = loader.get_template_class(template[layout.card_class])
    else: card_template = loader.get_template(template, layout.card_class)

    if card_template:

        # Include collector number
        try: layout.collector_number = scryfall['collector_number']
        except: layout.collector_number = None

        # Include creator
        if card['creator']: layout.creator = card['creator']
        else: layout.creator = None

        # Select and execute the template
        card_template(layout, file).execute()

    else:

        # No matching template
        input("No template found for layout: {layout.card_class}\nPress enter to exit...")
        exit()
