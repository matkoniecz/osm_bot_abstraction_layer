from osm_bot_abstraction_layer.generic_bot_retagging import run_simple_retagging_task
from osm_bot_abstraction_layer.utils import tag_in_wikimedia_syntax

def fix_bad_values(editing_on_key, replacement_dictionary, cache_folder_filepath, is_in_manual_mode, discussion_url, osm_wiki_documentation_page):
    """
    example:
    editing_on_key = "shop"
    replacement_dictionary = {'coal': {'shop': 'fuel', 'fuel': 'coal'}}
    """
    if(len(replacement_dictionary) == 0):
        return
    show_what_will_be_edited(editing_on_key, replacement_dictionary)
    query = """
[out:xml][timeout:1800];
(
"""
    for value in replacement_dictionary.keys():
        query += "  nwr['" + editing_on_key + "'='" + value + "'];\n"
    query += """);
out body;
>;
out skel qt;
"""
    run_simple_retagging_task(
        max_count_of_elements_in_one_changeset=500,
        objects_to_consider_query=query,
        cache_folder_filepath=cache_folder_filepath,
        is_in_manual_mode=is_in_manual_mode,
        changeset_comment='cleanup objects tagged with unusual and replaceable ' + editing_on_key + ' values (like ' + editing_on_key + '=' + list(replacement_dictionary.keys())[0] + ')',
        discussion_url=discussion_url,
        osm_wiki_documentation_page=osm_wiki_documentation_page,
        edit_element_function=edit_element_factory(editing_on_key, replacement_dictionary),
    )

def show_what_will_be_edited(key, replacement_dictionary):
    for replaced_value, new_values_dictionary in replacement_dictionary.items():
        new_content = ""
        for new_key, new_value in new_values_dictionary.items():
            new_content += new_key + " = " + new_value + " "
        print(key, "=", replaced_value, "→", new_content)

    for replaced_value, new_values_dictionary in replacement_dictionary.items():
        new_content = ""
        for new_key, new_value in new_values_dictionary.items():
            new_content += tag_in_wikimedia_syntax(new_key, new_value) + " "
        print("*", tag_in_wikimedia_syntax(key, replaced_value), "→", new_content)

def edit_element_factory(editing_on_key, replacement_dictionary):
    def edit_element(tags):
        if tags.get(editing_on_key) in replacement_dictionary:
            case = replacement_dictionary[tags.get(editing_on_key)]
            print(case)
            if tags.get(editing_on_key) in tags:
                print("skipping as there is a cascading tagging here and we would break it")
                print("there is")
                print(editing_on_key, "=", tags.get(editing_on_key))
                print(tags.get(editing_on_key), "=", tags.get(tags.get(editing_on_key)))
                print(tags)
                return tags
            for key, value in case.items():
                value_being_changed = tags.get(key)
                print("new tag:", key, "=", value)
                print("current tag for this key:", key, "=", value_being_changed)
                if key in tags:
                    # if it is empty we can just set a new value and this is not a problem
                    if key == editing_on_key:
                        # we can edit key explicitly being edited
                        # we still want to skip possibly unexpected changes
                        continue
                    if value_being_changed != value:
                        print("conflict between requested", key, "=", value, " and already present", key, "=", value_being_changed)
                        return tags
            tags.pop(editing_on_key)
            for key, value in case.items():
                tags[key] = value
            return tags
        return tags
    return edit_element
