from osm_bot_abstraction_layer.generic_bot_retagging import run_simple_retagging_task

def fix_bad_values(editing_on_key, replacement_dictionary, cache_folder_filepath, is_in_manual_mode, discussion_url, osm_wiki_documentation_page):
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

def edit_element_factory(editing_on_key, replacement_dictionary):
    def edit_element(tags):
        if tags.get(editing_on_key) in replacement_dictionary:
            case = replacement_dictionary[tags.get(editing_on_key)]
            print(case)
            for key, value in case.items():
                print(key, "=", value)
                print(tags.get(key))
                if key in tags:
                    if key == editing_on_key:
                        # that can be changed
                        continue
                    if tags.get(key) != value:
                        print("conflict")
                        return tags
            tags.pop(editing_on_key)
            for key, value in case.items():
                tags[key] = value
            return tags
        return tags
    return edit_element
