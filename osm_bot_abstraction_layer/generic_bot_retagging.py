import osm_bot_abstraction_layer.overpass_downloader as overpass_downloader
import osm_bot_abstraction_layer.osm_bot_abstraction_layer as osm_bot_abstraction_layer
import osm_bot_abstraction_layer.human_verification_mode as human_verification_mode
from osm_bot_abstraction_layer.split_into_packages import Package
from osm_iterator.osm_iterator import Data
import time

def splitter_generator(edit_element):
    def splitter_generated(element):
        global list_of_elements
        global checked_element_count
        checked_element_count += 1

        tag_dictionary = element.get_tag_dictionary()
        old = dict(tag_dictionary)
        if old != edit_element(tag_dictionary):
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

def process_osm_elements_package(package, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function):
    api = build_changeset(is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page)
    for element in package.list:
        data = modify_data_locally_and_show_changes(element.get_link(), edit_element_function)
        if is_edit_allowed(is_in_manual_mode, element.get_link()):
            osm_bot_abstraction_layer.update_element(api, element.element.tag, data)
        print()
        print()
    api.ChangesetClose()
    sleep_after_edit(is_in_manual_mode)

def is_edit_allowed(is_in_manual_mode, link):
    if is_in_manual_mode == False:
        return True
    return human_verification_mode.is_human_confirming(link)

def modify_data_locally_and_show_changes(osm_link_to_object, edit_element_function):
    prerequisites = {}
    data = osm_bot_abstraction_layer.get_and_verify_data(osm_link_to_object, prerequisites)

    human_verification_mode.smart_print_tag_dictionary(data['tag'])

    old = dict(data['tag'])
    data['tag'] = edit_element_function(data['tag'])
    if old == data['tag']:
        # may be not editable in case of lags in Overpass API database
        # or concurrent edits 
        print("Element has new version no longer eligible for an edit!")
        print("Probably Overpass returned outdated data! There is a concurrent edit!")
        raise RuntimeError
    print()
    human_verification_mode.smart_print_tag_dictionary(data['tag'])
    return data

def sleep_after_edit(is_in_manual_mode):
    if is_in_manual_mode:
        return
    time.sleep(60)

def show_planned_edits(packages, edit_element_function):
    for package in packages:
        for element in package.list:
            print("#", element.get_link())
            before = element.get_tag_dictionary()
            after = edit_element_function(element.get_tag_dictionary())
            if after == None:
                raise ValueError("edit_element_function returned None, it must return dictionary representing tags")
            for key in before.keys():
                if key not in after:
                    print("#* removed:", key,"=", before[key])
                elif before[key] != after[key]:
                    print("#* changed:", key)
                    print("#** before:", key,"=", before[key])
                    print("#** after_:", key,"=", after[key])
            for key in after.keys():
                if key not in before:
                    print("#* added_:", key,"=", after[key])
            print()

def run_actual_edits(packages, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function):
    for package in packages:
        for element in package.list:
            print(element.get_link())
        process_osm_elements_package(package, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function)
        print()
        print()

def run_simple_retagging_task(max_count_of_elements_in_one_changeset, objects_to_consider_query,
    objects_to_consider_query_storage_file, is_in_manual_mode,
    changeset_comment, discussion_url, osm_wiki_documentation_page,
    edit_element_function):
    overpass_downloader.download_overpass_query(objects_to_consider_query, objects_to_consider_query_storage_file)

    global list_of_elements
    global checked_element_count
    list_of_elements = []
    checked_element_count = 0

    osm = Data(objects_to_consider_query_storage_file)
    osm.iterate_over_data(splitter_generator(edit_element_function))

    packages = Package.split_into_packages(list_of_elements, max_count_of_elements_in_one_changeset)
    if len(list_of_elements) == 0:
        print("no elements found for editing among", checked_element_count, "checked items, skipping!")
        return
    show_planned_edits(packages, edit_element_function)
    print(str(len(list_of_elements)) + " objects split into " + str(len(packages)) + " edits. Continue? [y/n]")
    if human_verification_mode.is_human_confirming(link=None) == False:
        return
    run_actual_edits(packages, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function)
