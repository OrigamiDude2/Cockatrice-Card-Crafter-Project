from dearpygui.core import *
from dearpygui.simple import *
import pip._vendor.requests as requests
import os,time,bs4, json
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq


# ===========Main Variables==============#
# Main Window where widget opens!
set_main_window_size(width=700,height=700)
QuestionSpacing = 3
#Card Pic Scale
scale = 3
intro = "Please check and fill out each category below:"
card_data = None
save_data = None



#=============================Helper Methods===============================#


#====================Call Back Methods===================#

list ={}

# Takes revised and Submited Data and crafts card in XML format
def save_callback(sender, data):
    items = get_all_items()
    revised_items=[]
    for item in items:
        if(item.find('#')!=-1):
            revised_items.append(item)
    
    for item in revised_items:
        list[item] = get_value(item)


    fileText=f"""<?xml version="1.0" encoding="UTF-8"?>
                <cockatrice_carddatabase version="4">
                        <sets>
                            <set>
                                <name>{list['##Set Code']}</name>
                                <longname>{list['##Set Description']}</longname>
                                <settype>{list['##Set Type']}</settype>
                                <releasedate>{list['##Set Release Date']}</releasedate>
                            </set>	
                        </sets>
                        <cards>
                            <card>
                                <name>{list['##Card Name']}</name>
                                    <text>{findOracleText()}
                                    </text>
                                <prop>
                                    <layout>{list['##Card Layout']}</layout>
                                    <side>{list['##Card Side']}</side>
                                    <type>{list['##Card Type']}</type>
                                    <maintype>{findMainType()}</maintype>
                                    <manacost>{list['##Card Mana Cost']}</manacost>
                                    <cmc>{list['##Card Converted Mana Cost']}</cmc>
                                    <colors>{list['##Card Colors']}</colors>
                                    <coloridentity>{list['##Card Color Identity']}</coloridentity>
                                    {findPowerToughness()}
                                    {findLoyalty()}
                                </prop>
                                <set rarity="{list['##Card Rarity']}" uuid="{list['##Card Universal Unique Identifer']}" num="{list['##Card Collector Number']}" muid="{list['##Card Multiverse ID']}" picurl="{list['##url']}">{list['##Set Code']}</set>
                                {isToken()}
                                <tablerow>{rowFinder()}</tablerow>
                                {isTapped()}
                                {isFlipCard()}
                                {isRelatedCard()}
                                {isReverseRelatedCard()}
                            </card>
                        </cards>
                </cockatrice_carddatabase>"""
    
    # Removes all blank lines in string before it is saved to file
    fileText = "".join([s for s in fileText.strip().splitlines(True) if s.strip()])
    
    global save_data

    save_data = fileText
    
    # open file dialog box, find locatoin to save file and name file
    select_directory_dialog(callback=saveFile)
   
# Pulls info from Scryfall and loads into app
def apply_callback(sender,data):
        # Start Timer!
        tic = time.perf_counter()

        add_progress_bar('Loading Bar',parent='Card Crafter',before='ender')

        url = get_value('##url')

        #================Downloads the webpage of card from scryfall.com====================#
        uClient = uReq(url)
        
        # Dumps int variable
        page_html = uClient.read()
        uClient.close()

        AdvanceLoadingBar()

        # html parsing
        page_soup = soup(page_html,"html.parser")

        AdvanceLoadingBar()

        #finds link to Json file
        links = page_soup.find_all("a",{"class":"button-n","data-track":'{"category":"Card Detail","action":"Utility Link","label":"Card JSON"}'})

        JsonURL = links[0].get('href')

        #Downloads the webpage of json file
        uClient = uReq(JsonURL)

        AdvanceLoadingBar()
        
        # Dumps into variable
        page_html = uClient.read()
        uClient.close()

        AdvanceLoadingBar()

        json_file = soup(page_html,"html.parser")

        #loads the webage into a json file
        data_file = json.loads(str(json_file))

        global card_data 

        card_data = data_file

        AdvanceLoadingBar()

        toc = time.perf_counter()

        print("\n\n\n")
        print("================================================")
        print(f"Downloaded the data in {toc - tic:0.4f} seconds")
        print("================================================")

        AdvanceLoadingBar()


        #===========Fill Card Info into Text Boxes=============#
        try:
            set_value("##Set Code", card_data['set'].upper())
            set_value("##Set Description", str(card_data['set_name']))
            set_value("##Set Type", str(card_data['set_type']))
            set_value("##Set Release Date", str(card_data['released_at']))
            set_value("##Card Name", card_data['name'])
            set_value("##Card Description", card_data['oracle_text'])
            set_value("##Card Layout", card_data['layout'])
            set_value("##Card Side", "Front")
            set_value("##Card Type", card_data['type_line'])
        
            AdvanceLoadingBar()
            # create method to figure out :
            #set_value("##Card Main Type", card_data[''])
            set_value("##Card Mana Cost", card_data['mana_cost'])
            set_value("##Card Converted Mana Cost", str(card_data['cmc']))
            set_value("##Card Colors", card_data['colors'])
            set_value("##Card Color Identity", card_data['color_identity'])
            set_value("##Card Power and Toughness", f"{card_data['power']}/{card_data['toughness']}")
            try:
                set_value("##Card Starting Loyalty", card_data['loyalty'])
            except KeyError:
                set_value("##Card Starting Loyalty", "")
            set_value("##Card Rarity", card_data['rarity'])

            AdvanceLoadingBar()

            set_value("##Card Universal Unique Identifer", card_data['id'])
            if(len(card_data['multiverse_ids'])!=0): set_value("##Card Multiverse ID", card_data['multiverse_ids'])
            set_value("##Card Picture URL", card_data['image_uris']['png'])

            AdvanceLoadingBar()

            # picture drawing!
            url = card_data['image_uris']['png']
            # request the data from url
            r = requests.get(url, allow_redirects=True)
            # writes data to a file
            open('card.png', 'wb').write(r.content)
            # draws the image
            draw_image("image",file='card.png',pmin=[0.0,0.0],pmax=[745.0/scale,1040.0/scale])
            
        except KeyError:
            pass
        
        AdvanceLoadingBar()

        add_text("Download Complete!\n ",parent="Card Crafter",before='Loading Bar')


# Reloads the url of picture to be displayed
def reload_callback(sender,data):
    # picture drawing!
    url = get_value('##Card Picture URL')

    r = requests.get(url, allow_redirects=True)

    open('card.png', 'wb').write(r.content)

    clear_drawing('image')

    draw_image("image",file='card.png',pmin=[0.0,0.0],pmax=[745.0/scale,1040.0/scale])

def combo_callback(sender, data):
    print(get_value(sender))

def ok_callback(sender,data):
    print("I like to fuck some bitches up!")

    

#========================================================#

 

# Saves data to file from the directory call
def saveFile(sender,data):
    log_debug(data)  # so we can see what is inside of data
    directory = data[0]
    folder = data[1]
    path = f"{directory}\\{folder}\\{get_value('##file name')}.xml"

    file = open(path,'w')
    file.write(save_data)
    file.close()

# Checks for Related Card Data and inputs into main string file
def isRelatedCard():
    card_name = get_value('##Related Card Name')
    attachment = get_value('Card Attachment')
    if(attachment==0):
        attachment='attach'
    else:
        attachment=''
    count = get_value('##Number of Tokens Created')
    if(card_name!=''):
        return f"<related attach='{attachment}' count='{count}'>{card_name}</related>"
    else:
        return ""

# Checks for Reverse Related Card Data and inputs into main string file
def isReverseRelatedCard():
    card_name = get_value('##Reverse Related Card Name')
    if(card_name!=''):
        return f"<reverse-related>{card_name}</reverse-related>"
    else:
        return ""  

#Searches for the main type of the card in MTG:  
#lands, creatures, enchantments, artifacts, instants, and sorceries
def findMainType():

    text = list['##Card Type']

    if(text.find("Creature")!=-1): return "Creature"
    elif (text.find("Enchantment")!=-1): return "Enchantment"
    elif (text.find("Artifact")!=-1): return "Artifact"
    elif (text.find("Instant")!=-1): return "Instant"
    elif (text.find("Sorceries")!=-1): return "Sorceries"
    elif (text.find("Planeswalker")!=-1): return "Planeswalker"
    else: return "Land"

#find power and toughness of card if exists
def findPowerToughness():
    if(findMainType()!="Creature"): return ''
    else: 
        return f'<pt>{list["##Card Power and Toughness"]}</pt>'

#find starting loyalty of planeswalker if it exists
def findLoyalty():
    if(findMainType()!="Planeswalker"): return ''
    else: 
        return f'<loyalty>{list["##Card Starting Loyalty"]}</loyalty>'

# Detects whether the card is a token or not
def isToken():
    if(get_value('isToken')==0): return '<token>1</token>'
    else : return ''

# Finds what row number for the card type 
# so it can be organized properly in game
def rowFinder():
    text = findMainType()
    if(text == "Land"): return 0
    elif (text == 'Planeswalker' or text == 'Enchantment' or text =='Artifacts'): return 1
    elif (text == "Creature"): return 2
    else: return 3

# Detects whether the card is a flip card or not
def isFlipCard():
    if(get_value('isFlip')==0): return '<upsidedown>1</upsidedown>'
    else: return ''

# Detects whether the card comes into play tapped
def isTapped():
    text = findOracleText()

    if(text.find('comes into play tapped')!= -1 or text.find('enters the battlefield tapped')!=-1):
        return '<cipt>1</cipt>'
    else: return ''


# Finds the oracle text of card including if flip card
def findOracleText():
    if(list['##Card Layout']=='flip' or list['##Card Layout']=='modal_dfc'):
        card_faces = card_data['card_faces']
        top = card_faces[0]['oracle_text']
        bottom = card_faces[1]['oracle_text']
        oracle_text = f'{top} // {bottom}'
        return oracle_text
    else:
        return list['##Card Description']

progress=0.0
def AdvanceLoadingBar():
    global progress
    set_value('Loading Bar', progress)
    progress+=0.12
    print(progress)


#====================SET UP Main Window=================================#
with window("Card Crafter",width=665,height=500,x_pos=10,y_pos=10):

    add_text("Welcome to the Card Carfter 3.0")

    add_spacing(count=QuestionSpacing)

    add_text("Please enter the url below: ")
    add_input_text("##url")
    set_value("##url", "https://scryfall.com/card/khc/1/lathril-blade-of-the-elves")
    add_spacing(count=QuestionSpacing)
    add_button("Apply",callback=apply_callback)   
    add_spacing(count=QuestionSpacing)    
    add_separator(name="ender")


    #====================SET INFO======================================#
    with collapsing_header("Set Information"):
        add_text(intro)
        add_spacing(count=QuestionSpacing)

        add_text("Set Code: ")
        add_input_text("##Set Code",tip="The 3 letter code for the set;\n Kalhiem set code: KHM")

        add_spacing(count=QuestionSpacing)

        add_text("Set Description: ")
        add_input_text("##Set Description",tip="Full Name of Set")

        add_spacing(count=QuestionSpacing)
        
        # Add combo box instead of text input?
        add_text("Set Type: ")
        add_input_text("##Set Type",tip="Type Sets: \nCore\nExpansion\nPromo")

        add_spacing(count=QuestionSpacing)

        add_text("Set Release Date: ")
        add_input_text("##Set Release Date",tip="The date of when the set was released.\n Format: mm-dd-yyyy")
        
        add_spacing(count=QuestionSpacing)

        add_separator()
        add_spacing(count=1)

    #====================Card INFO=====================================#    
    with collapsing_header("Card Information"):
        add_text(intro)
        add_spacing(count=QuestionSpacing)

        add_text("Card Name: ")
        add_input_text("##Card Name",tip="Name of the Card; Can be found at the top of the card")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Description: ")
        add_input_text("##Card Description",tip="The oracle text, ability, and effects",multiline=True)
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Layout: ")
        add_input_text("##Card Layout",tip="Card Layout Types:\nnormal\nsplit\ntransform\nflip\nmodal dual faced")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Side: ")
        add_input_text("##Card Side",tip="eg Front or Back of Card")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Type: ")
        add_input_text("##Card Type",tip="The full type of the card, eg. Legendary Creature — Spirit Cleric")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Main Type: ")
        add_input_text("##Card Main Type",tip="The main type of the card, eg. Creature, Sorcery, Instant, Land, etc")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Mana Cost: ")
        add_input_text("##Card Mana Cost",tip="Card mana cost, eg. 1WU")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Converted Mana Cost: ")
        add_input_text("##Card Converted Mana Cost",tip="Card converted mana cost, eg. 3")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Colors: ")
        add_input_text("##Card Colors",tip="If colorless leave blank")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Color Identity: ")
        add_input_text("##Card Color Identity",tip="If colorless leave blank")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Power and Toughness: ")
        add_input_text("##Card Power and Toughness",tip="If the card does not have p/t please leave blank")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Starting Loyalty: ")
        add_input_text("##Card Starting Loyalty",tip="If the card has no loyalty counters please leave blank")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Rarity: ")
        add_input_text("##Card Rarity",tip="Rarity Types: \nCommon\nUncommon\nRare\nMythic Rare")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Universal Unique Identifer: ")
        add_input_text("##Card Universal Unique Identifer",tip="A universally unique identifier of this card in this set that must be unique for every single card. \nThis can be used to reference the card on external resources, eg. to load a card picture from a website.")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Collector Number: ")
        add_input_text("##Card Collector Number",tip="The card's collector number in the set. This can be used to reference\n the card on external resources, eg. to load a card picture from a website.")
        
        add_spacing(count=QuestionSpacing)

        add_text("Card Multiverse ID: ")
        add_input_text("##Card Multiverse ID",tip="The card's multiverse id. This is a special code assigned to each card in a specific game")
        
        add_spacing(count=QuestionSpacing)

        # Draw out the url picture so easy to confirm correct link!
        add_text("Card Picture URL: ")
        add_input_text("##Card Picture URL",tip="If the picture below is not correct, please retype the url and hit 'Enter' to reload the image", callback=reload_callback,on_enter=True)
        
        add_spacing(count=QuestionSpacing)

        add_drawing('image', width=int(1000/scale),height=int(1000/scale))

        add_separator(name='seperator1')
        add_spacing(count=1)

    #====================Card Relationship INFO========================#
    with collapsing_header("Relationship Card Information"):
        add_text(intro)
        add_spacing(count=QuestionSpacing)

        add_text("Is this card a Token? ")
        add_radio_button("isToken",items=["Yes","No",],horizontal=True)

        add_spacing(count=QuestionSpacing)
        
        add_text("Is this card a flip card? ")
        add_radio_button("isFlip",items=["Yes","No"],horizontal=True)

        add_spacing(count=QuestionSpacing)

        # Adjust the creation of these text boxes depending on the user answer
        add_text("Related Card Name: ")
        add_input_text("##Related Card Name",tip="If the card can create or transform itself into another card \n(eg. create a token, flip, or dual faced), Please type the name of the related card or token")

        add_spacing(count=QuestionSpacing)

        add_text("Number of Tokens Created: ")
        add_input_text("##Number of Tokens Created",tip="Number of tokens created from spell; \n If card creates X amount of tokens please type 1!")

        add_spacing(count=QuestionSpacing)

        add_text("Card Attachment: ")
        add_radio_button("Card Attachment", items=['Yes','No'],tip="If the created card must be attached to the original card")

        add_spacing(count=QuestionSpacing)      

        add_text("Reverse Related Card Name: ")
        add_input_text("##Reverse Related Card Name",tip="if the card can be created by another card \n(eg. this card is a token that can be created by another card)")

        add_spacing(count=QuestionSpacing)


    #====================Submit Section================================#
    add_separator()
    add_spacing(count=3)

    add_text("Please type the name of the Save File below")
    add_input_text('##file name',hint='Please type file name here')
    add_button("Save", callback = save_callback)


    
    #+++++++++++++++++++++Testing Code Area++++++++++++++++++++++++++++#

    #combo box
    #add_combo("combo box", items=['1','2','3','4','5'],callback=combo_callback)

    # Radio Buttons

    
#============RUN THE APP=========#

start_dearpygui() 

#============CLOSING THE APP======#


if os.path.exists("card.png"):
  os.remove("card.png")
else:
  print("The file does not exist")