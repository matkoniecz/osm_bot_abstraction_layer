import osm_bot_abstraction_layer.overpass_downloader as overpass_downloader
import osm_bot_abstraction_layer.osm_bot_abstraction_layer as osm_bot_abstraction_layer
import osm_bot_abstraction_layer.human_verification_mode as human_verification_mode
from osm_bot_abstraction_layer.split_into_packages import Package
from osm_iterator.osm_iterator import Data
import time

def splitter_generator(is_element_editable_function):
    def splitter_generated(element):
        global list_of_elements
        if is_element_editable_function(element.get_tag_dictionary(), element.get_link()):
            list_of_elements.append(element)
    return splitter_generated # returns a callback function

def build_changeset(is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page):
    automatic_status = osm_bot_abstraction_layer.manually_reviewed_description()
    if is_in_manual_mode == False:
        automatic_status = osm_bot_abstraction_layer.fully_automated_description()
    comment = changeset_comment
    source = None
    api = osm_bot_abstraction_layer.get_correct_api(automatic_status, discussion_url)
    affected_objects_description = ""
    builder = osm_bot_abstraction_layer.ChangesetBuilder(affected_objects_description, comment, automatic_status, discussion_url, osm_wiki_documentation_page, source)
    builder.create_changeset(api)
    return api

def process_osm_elements_package(package, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function, is_element_editable_function):
    api = build_changeset(is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page)
    for element in package.list:
        data = modify_data_locally_and_show_changes(element.get_link(), edit_element_function, is_element_editable_function)
        if is_edit_allowed(is_in_manual_mode):
            osm_bot_abstraction_layer.update_element(api, element.element.tag, data)
        print()
        print()
    api.ChangesetClose()
    sleep_after_edit(is_in_manual_mode)

def is_edit_allowed(is_in_manual_mode):
    if is_in_manual_mode == False:
        return True
    return human_verification_mode.is_human_confirming()

def modify_data_locally_and_show_changes(osm_link_to_object, edit_element_function, is_element_editable_function):
    prerequisites = {}
    data = osm_bot_abstraction_layer.get_and_verify_data(osm_link_to_object, prerequisites)

    human_verification_mode.smart_print_tag_dictionary(data['tag'])

    if not is_element_editable_function(data['tag'], "test before edit"):
        # may be not editable in case of lags in Overpass API database
        # or concurrent edits 
        print("Element has new version no longer eligible for an edit!")
        print("Probably Overpass returned outdated data! There is a concurrent edit!")
        raise RuntimeError

    data['tag'] = edit_element_function(data['tag'])
    print()
    human_verification_mode.smart_print_tag_dictionary(data['tag'])
    return data

def sleep_after_edit(is_in_manual_mode):
    if is_in_manual_mode:
        return
    time.sleep(60)

def run_simple_retagging_task(max_count_of_elements_in_one_changeset, objects_to_consider_query,
    objects_to_consider_query_storage_file, is_in_manual_mode,
    changeset_comment, discussion_url, osm_wiki_documentation_page, is_element_editable_checker_function,
    edit_element_function):
    overpass_downloader.download_overpass_query(objects_to_consider_query, objects_to_consider_query_storage_file)

    global list_of_elements
    list_of_elements = []

    osm = Data(objects_to_consider_query_storage_file)
    osm.iterate_over_data(splitter_generator(is_element_editable_checker_function))

    packages = Package.split_into_packages(list_of_elements, max_count_of_elements_in_one_changeset)
    if len(list_of_elements) == 0:
        print("no elements found, skipping!")
        return
    print(str(len(list_of_elements)) + " objects split into " + str(len(packages)) + " edits. Continue? [y/n]")
    if human_verification_mode.is_human_confirming() == False:
        return
    for package in packages:
        for element in package.list:
            print(element.get_link())
        process_osm_elements_package(package, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function, is_element_editable_checker_function)
        print()
        print()
