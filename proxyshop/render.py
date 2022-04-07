"""
INITIATE AND PREPARE RENDER JOB
"""
import os
import re
from timeit import default_timer as timer
from datetime import timedelta
from proxyshop import layouts, core
import proxyshop.constants as con
import proxyshop.scryfall as scry
import proxyshop.helpers as psd

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


def render (file,template,previous):
    """
    Set up this render job, then execute
    """
    # pylint: disable=R0912, R1722
    start = timer()
    card = retrieve_card_info(os.path.basename(str(file)))

    # If basic, manually call the BasicLand layout OBJ
    if card['name'] in con.basic_land_names:
        layout = layouts.BasicLand(card['name'], card['artist'], card['set'])
    else:

        # Get the scryfall info
        scryfall = scry.card_info(card['name'], card['set'])

        # Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
        try: layout = layouts.layout_map[scryfall['layout']](scryfall, card['name'])
        except: core.handle(f"Layout '{scryfall['layout']}' is not supported.")

        # If artist specified in file name, replace artist in layout OBJ
        if card['artist']: layout.artist = card['artist']

        # Get full set info from scryfall
        mtgset = scry.set_info(layout.set)

        # Set up the card count of the set
        layout.card_count = "XXX"
        try: layout.card_count = mtgset['printed_size']
        except:
            try: layout.card_count = mtgset['card_count']
            except: pass

    # Get our template and layout class maps
    if isinstance(template, dict):
        card_template = core.get_template(template[layout.card_class])
    else: card_template = core.get_template(template, layout.card_class)

    if card_template:

        # Close the open document if current template aligns with previous
        if previous is not None:
            if previous is not card_template:
                try: psd.close_document()
                except: pass

        # Include collector number
        try: layout.collector_number = scryfall['collector_number']
        except: layout.collector_number = None

        # Include creator
        if card['creator']: layout.creator = card['creator']
        else: layout.creator = None

        # Select and execute the template
        result = card_template(layout, file).execute()

    else: core.handle("No template found for layout: {layout.card_class}")

    # Timer result, return template class
    end = timer()
    if result:
        print("Time completed: "+str(timedelta(seconds=end-start))[2:-7]+"\n")
        return card_template
    return None

def render_custom (file,template,scryfall):
    """
    Set up this render job, then execute
    """
    # pylint: disable=R0912, R1722
    start = timer()

    # If basic, manually call the BasicLand layout OBJ
    if scryfall['name'] in con.basic_land_names:
        layout = layouts.BasicLand(scryfall['name'], scryfall['artist'], scryfall['set'])
    else:

        # Instantiate layout OBJ, unpack scryfall json and store relevant data as attributes
        try: layout = layouts.layout_map[scryfall['layout']](scryfall, scryfall['name'])
        except: core.handle(f"Layout '{scryfall['layout']}' is not supported.")

    # Get our template and layout class maps
    if isinstance(template, list): card_template = core.get_template(template)
    else: core.handle("Template not found!")

    if card_template:

        # Additional variables
        layout.card_count = scryfall['card_count']
        layout.collector_number = scryfall['collector_number']
        layout.creator = None

        # Select and execute the template
        card_template(layout, file).execute()

    else: core.handle("No template found for layout: {layout.card_class}")
    # Execution time
    end = timer()
    print("Time completed: "+str(timedelta(seconds=end-start))[2:-7]+"\n")
