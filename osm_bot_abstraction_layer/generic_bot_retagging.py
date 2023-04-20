import osm_bot_abstraction_layer.overpass_downloader as overpass_downloader
import osm_bot_abstraction_layer.osm_bot_abstraction_layer as osm_bot_abstraction_layer
import osm_bot_abstraction_layer.human_verification_mode as human_verification_mode
from osm_bot_abstraction_layer.split_into_packages import Package
from osm_iterator.osm_iterator import Data
import time
import osmapi
import webbrowser
import hashlib
import taginfo

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
    if len(changeset_comment) < 4:
        raise Exception("changeset_comment is unreasonably short: " + changeset_comment)
    automatic_status = osm_bot_abstraction_layer.manually_reviewed_description()
    if is_in_manual_mode == False:
        automatic_status = osm_bot_abstraction_layer.fully_automated_description()
    comment = changeset_comment
    source = None
    api = osm_bot_abstraction_layer.get_correct_api(automatic_status, discussion_url, osm_wiki_documentation_page)
    affected_objects_description = ""
    builder = osm_bot_abstraction_layer.ChangesetBuilder(affected_objects_description, comment, automatic_status, discussion_url, osm_wiki_documentation_page, source)
    builder.create_changeset(api)
    return api

def has_nearby_notes(osm_link_to_object):
    for node in osm_bot_abstraction_layer.get_all_nodes_of_an_object(osm_link_to_object):
        data = osm_bot_abstraction_layer.get_data(node, "node")
        lat = data["lat"]
        lon = data["lon"]
        min_lat = lat - 0.01
        max_lat = lat + 0.01
        min_lon = lon - 0.01
        max_lon = lon + 0.01
        notes = osm_bot_abstraction_layer.get_notes_in_area(min_lon, min_lat, max_lon, max_lat, limit=1)
        print(notes)
        print(len(notes))
        if len(notes) > 0:
            print("https://www.openstreetmap.org/note/" + notes[0]["id"])
            return True
    return False

def process_osm_elements_package(package, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function, skip_on_nearby_notes):
    changeset = None
    for element in package.list:

        if skip_on_nearby_notes:
            if has_nearby_notes(element.get_link()):
                continue

        data = modify_data_locally_and_show_changes(element.get_link(), edit_element_function)
        if is_in_manual_mode:
            webbrowser.open(element.get_history_link(), new=2)
        if is_edit_allowed(is_in_manual_mode, element.get_id_edit_link()):
            retry_remaining_attempts = 5
            while retry_remaining_attempts > 0:
                retry_remaining_attempts -= 1
                try:
                    if changeset == None:
                        changeset = build_changeset(is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page)
                    osm_bot_abstraction_layer.update_element(changeset, element.element.tag, data)
                    break # completed succesfully, no need to repeat
                except osmapi.ApiError as e:
                    if is_exception_about_already_closed_changeset(e):
                        changeset = None
                        continue # ugly but... https://stackoverflow.com/a/2083996/4130619
                    else:
                        print("error! Paused for review. Press enter to continue.")
                        input()
                except Exception as e:
                    print("some other exception happened in process_osm_elements_package", e)
                    raise e
        print()
        print()
    try:
      if changeset != None:
        changeset.ChangesetClose()
    except osmapi.ApiError as e:
      if is_exception_about_already_closed_changeset(e):
        pass
      else:
        raise e
    sleep_after_edit(is_in_manual_mode)

def is_exception_about_already_closed_changeset(exception):
    print(str(exception))
    print("was closed at" in str(exception))
    print("******")
    if "was closed at" in str(exception): # there is no more specific exception... https://github.com/metaodi/osmapi/issues/115
      return True
    else:
      return False

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
        error = "Element has new version - no longer eligible for an edit! \n Probably Overpass returned outdated data! There is a concurrent edit!\n\nNote also database lag - see https://wiki.openstreetmap.org/wiki/Overpass_API#Limitations"
        raise RuntimeError(error)
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

def run_actual_edits(packages, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function, skip_on_nearby_notes):
    for package in packages:
        for element in package.list:
            print(element.get_link())
        process_osm_elements_package(package, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function, skip_on_nearby_notes)
        print()
        print()

def run_simple_retagging_task(max_count_of_elements_in_one_changeset, objects_to_consider_query,
    cache_folder_filepath, is_in_manual_mode,
    changeset_comment, discussion_url, osm_wiki_documentation_page,
    edit_element_function, skip_on_nearby_notes=False):
    hashed = hashlib.sha256(objects_to_consider_query.encode('utf-8')).hexdigest()
    if cache_folder_filepath[-1] == "/":
        raise Exception("provide folder path without trailing /")
    objects_to_consider_query_storage_file = cache_folder_filepath + '/downloaded_data_' + hashed + '.osm'
    overpass_downloader.download_overpass_query(objects_to_consider_query, objects_to_consider_query_storage_file)

    global list_of_elements
    global checked_element_count
    list_of_elements = []
    checked_element_count = 0

    osm = Data(objects_to_consider_query_storage_file)
    osm.iterate_over_data(splitter_generator(edit_element_function))

    # list_of_elements is filled with above function, elements are osm_iterator.Element objects
    packages = Package.split_into_packages(list_of_elements, max_count_of_elements_in_one_changeset)
    if len(list_of_elements) == 0:
        print("no elements found for editing among", checked_element_count, "checked items, skipping!")
        return
    show_planned_edits(packages, edit_element_function)
    if is_in_manual_mode:
        print(str(len(list_of_elements)) + " objects will be split into " + str(len(packages)) + " edits.")
    else:
        print(str(len(list_of_elements)) + " objects split into " + str(len(packages)) + " edits. Continue? [y/n]")
        if human_verification_mode.is_human_confirming(link=None) == False:
            return
    run_actual_edits(packages, is_in_manual_mode, changeset_comment, discussion_url, osm_wiki_documentation_page, edit_element_function, skip_on_nearby_notes)

def check_value_list_before_bot_edit_proposal(key, value_list):
    """
    will complain about proposing to migrate unused keys
    will complain when high use ones are not listed near beginning
    """
    some_migrated_values_are_not_used_at_all = False
    some_popular_migrated_values_are_not_listed_near_start = False
    usage_count = {}
    for entry in taginfo.query.values_of_key_with_data(key):
        usage_count[entry['value']] = entry['count']
    total_usage = 0
    for old in value_list:
        if old not in usage_count:
            print(old, "has no use at all")
            some_migrated_values_are_not_used_at_all = True
        else:
            total_usage += usage_count[old]
        #elif usage_count[old] <= 3:
        #    print(old, "used just", usage_count[old], "times")
    threshold = total_usage * 4.0 / len(value_list)
    high_use_ones_header_shown = False
    for index, old in enumerate(value_list):
        if old not in usage_count:
            some_migrated_values_are_not_used_at_all = True
        elif usage_count[old] > threshold:
            if high_use_ones_header_shown == False:
                print("tags with highest use, among ones that will be retagged")
                high_use_ones_header_shown = True
            print(key, "=", old, "with", usage_count[old], "uses")
            threshold_position = int(len(value_list)/8)
            if index > threshold_position:
                print("and hiding in tail of a list, at position", index, "(was expected before " + str(threshold_position) + ")")
                some_popular_migrated_values_are_not_listed_near_start = True
    if high_use_ones_header_shown == False:
        print("no tag is used noticeable more often than others listed here")
    if some_migrated_values_are_not_used_at_all:
        raise Exception("some_migrated_values_are_not_used_at_all")
    if some_popular_migrated_values_are_not_listed_near_start:
        raise Exception("some values with high use are not listed at beginning of the list")
