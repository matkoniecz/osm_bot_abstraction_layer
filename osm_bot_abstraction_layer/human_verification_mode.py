import webbrowser
import osm_bot_abstraction_layer.tag_knowledge as tag_knowledge
from termcolor import colored

def is_human_confirming(link):
    if link != None:
        webbrowser.open(link, new=2)
    print("y + enter to confirm, anything else to reject")
    choice = input().lower()
    if choice == "y":
        return True
    return False

def smart_print_tag_dictionary(tags, special_expected={}):
    for key, value in sorted(tags.items()):
        text = key + "=" + value
        if tag_knowledge.is_expected_tag(key, value, tags, special_expected):
            print(text)
        else:
            print(colored(text, 'yellow'))

