import webbrowser
import osm_bot_abstraction_layer.tag_knowledge as tag_knowledge
from termcolor import colored

def is_human_confirming_without_browser_check(link=None):
    print("y + enter to confirm, anything else to reject")
    choice = input().lower()
    if choice == "y":
        return True
    return False

def is_human_confirming(link):
    if link == None:
        raise Exception("use is_human_confirming_without_browser_check")
    webbrowser.open(link, new=2)
    return is_human_confirming_without_browser_check(link)

def smart_print_tag_dictionary(tags, special_expected={}):
    for key, value in sorted(tags.items()):
        text = key + "=" + value
        if tag_knowledge.is_expected_tag(key, value, tags, special_expected):
            print(text)
        else:
            print(colored(text, 'yellow'))

