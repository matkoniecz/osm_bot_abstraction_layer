from osm_bot_abstraction_layer.generic_bot_retagging import run_simple_retagging_task
from osm_bot_abstraction_layer.utils import tag_in_wikimedia_syntax

def edit_element_factory(editing_on_key, replacement_dictionary):
    def edit_element(tags):
        if tags.get(editing_on_key) in replacement_dictionary:
            if tags.get(editing_on_key) in tags:
                print("skipping as there is a cascading tagging here and we would break it")
                print("there is")
                print(editing_on_key, "=", tags.get(editing_on_key))
                print(tags.get(editing_on_key), "=", tags.get(tags.get(editing_on_key)))
                print(tags)
                return tags
            tags[editing_on_key] = replacement_dictionary[tags[editing_on_key]]
            return tags
        return tags
    return edit_element

def list_what_will_be_edited(key, replacement_dictionary):
    returned = ""
    # markdown
    for replaced_value, new_value in replacement_dictionary.items():
        returned += '`' + key + " = " + replaced_value + "` → `" + key + " = " + new_value + "`\n"
    returned += "\n\n"

    # text
    for replaced_value, new_value in replacement_dictionary.items():
        returned += key + " = " + replaced_value + " → " + key + " = " + new_value + "\n"
    returned += "\n\n"

    # wiki
    for replaced_value, new_value in replacement_dictionary.items():
        returned += "* " + tag_in_wikimedia_syntax(key, replaced_value) + " → " + tag_in_wikimedia_syntax(key, new_value) + "\n"
    return returned

def fix_bad_values(editing_on_key, replacement_dictionary, cache_folder_filepath, is_in_manual_mode, discussion_url, osm_wiki_documentation_page):
    print(list_what_will_be_edited(editing_on_key, replacement_dictionary))
    edit_element_function = edit_element_factory(editing_on_key, replacement_dictionary)
    query = get_query(editing_on_key, replacement_dictionary)
    run_simple_retagging_task(
        max_count_of_elements_in_one_changeset=500,
        objects_to_consider_query=query,
        cache_folder_filepath=cache_folder_filepath,
        is_in_manual_mode=is_in_manual_mode,
        changeset_comment='fixing unusual ' + editing_on_key + ' values with a clear replacement',
        discussion_url=discussion_url,
        osm_wiki_documentation_page=osm_wiki_documentation_page,
        edit_element_function=edit_element_function,
    )

def get_query(editing_on_key, replacement_dictionary):
    backslash = "\\"
    query = ""
    query += "[out:xml][timeout:1800];\n"
    query += "(\n"
    for from_value, to_value in replacement_dictionary.items():
        escaped_key = editing_on_key.replace(backslash, backslash+backslash)
        escaped_value = from_value.replace(backslash, backslash+backslash)
        escaped_value = escaped_value.replace("'", backslash+"'")
        query += "  nwr['" + escaped_key + "'='" + escaped_value + "'];\n"
    query += ");\n"
    query += "out body;\n"
    query += ">;\n"
    query += "out skel qt;\n"
    return query
