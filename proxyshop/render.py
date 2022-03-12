"""
INITIATE AND PREPARE RENDER JOB
"""
import os
import re
import proxyshop.layouts as layouts
import proxyshop.constants as con
import proxyshop.settings as cfg
import proxyshop.scryfall as scry
import plugins.loader as loader
from proxyshop.helpers import save_and_close

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
    set = re.findall(r'\[+(.*?)\]', filename)

    # Check for these values
    if creator: creator = creator[0]
    else: creator = None
    if artist: artist = artist[0]
    else: artist = None
    if set: set = set[0]
    else: set = None
    
    return {
        'name': name,
        'artist': artist,
        'set': set,
        'creator': creator
    }


def render (file,template):
    """
    Set up this render job, then execute
    """
    # TODO: specify the desired template for a card in the filename?
    card = retrieve_card_info(os.path.basename(str(file)))

    if card['name'] in con.basic_land_names:

        # Manually construct layout obj for basic lands
        try: artist = card['artist']
        except: artist = "Unknown"
        layout = layouts.BasicLand(card['artist'], card['name'], con.basic_class, card['set'].upper())

    else:

        # Get the scryfall info
        scryfall = scry.card_info(card['name'], card['set'])
        scryfall = scry.preprocess(scryfall)
        layout_name = scryfall['layout']

        # instantiate layout obj (unpacks scryfall json and stores relevant parts in obj properties)
        try: layout = layouts.layout_map[scryfall['layout']](scryfall, card['name'])
        except: print("Layout" + layout_name + " is not supported. Sorry!")

        # if artist specified in file name, insert the specified artist into layout obj
        if card['artist']: layout.artist = card['artist']

        # Include setcode
        try: layout.set = card['set'].upper()
        except: 
            try: layout.set = scryfall['set'].upper()
            except: layout.set = "MTG"

        # Get full set info from scrython
        try: mtgset = scry.set_info(layout.set)
        except: mtgset = "MTG"
        if 'printed_size' in mtgset: layout.card_count = mtgset['printed_size']
        elif 'card_count' in mtgset: layout.card_count = mtgset['card_count']
        else: layout.card_count = "XXX"
    
    # Get our template and layout class maps
    if type(template) is str: card_template = loader.get_template(template, layout.card_class)
    elif template == None: card_template = loader.get_template(template, layout.card_class)
    else: card_template = loader.get_template_class(template[layout.card_class])

    if card_template:
        
        # Include collector number
        try: layout.collector_number = scryfall['collector_number']
        except: layout.collector_number = None
        
        # Include creator
        if card['creator']: layout.creator = card['creator']
        else: layout.creator = None
        
        # select and execute the template - insert text fields, set visibility of layers, etc. - and save to disk
        file_name = card_template(layout, file).execute()
        save_and_close(file_name)

    else:

        # No matching template
        print("No template found for layout: {layout.card_class}\nExiting now...")
        exit()