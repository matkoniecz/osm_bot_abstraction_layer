from osm_bot_abstraction_layer.generic_bot_retagging import run_simple_retagging_task
from osm_bot_abstraction_layer.utils import tag_in_wikimedia_syntax

def edit_element_factory(current_key, new_key):
    def edit_element(tags):
        if tags.get(current_key) == "yes":
            if tags.get(new_key) in ["yes", None]:
                tags.pop(current_key, None)
                tags[new_key] = "yes"
            else:
                print(new_key, "=", tags.get(new_key))
            return tags
        return tags
    return edit_element

def get_query(current_key):
    return """
[out:xml][timeout:1800];
(
  nwr['""" + current_key + """'=yes];
);
out body;
>;
out skel qt;
"""

def fix_bad_values(current_key, new_key, cache_folder_filepath, is_in_manual_mode, discussion_url, osm_wiki_documentation_page):
    edit_element_function = edit_element_factory(current_key, new_key)
    query = get_query(current_key)
    run_simple_retagging_task(
        max_count_of_elements_in_one_changeset=500,
        objects_to_consider_query=query,
        cache_folder_filepath=cache_folder_filepath,
        is_in_manual_mode=is_in_manual_mode,
        changeset_comment=current_key + '=yes -> ' + new_key + '=yes',
        discussion_url=discussion_url,
        osm_wiki_documentation_page=osm_wiki_documentation_page,
        edit_element_function=edit_element_function,
    )
