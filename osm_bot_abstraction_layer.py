# docs: http://osmapi.metaodi.ch/
import osmapi
import time

def bot_username():
    return "Mateusz Konieczny - bot account"

def manual_username():
    return "Mateusz Konieczny"

def fully_automated_description():
    return "yes"

def manually_reviewed_description():
    return "no, it is a manually reviewed edit"

def get_api(username):
    return osmapi.OsmApi(username = username, passwordfile = "password.secret")

def character_limit_of_description():
    return 255
 
class ChangesetBuilder:
    def __init__(self, affected_objects_description, comment, automatic_status, discussion_url, source):
        self.affected_objects_description = affected_objects_description
        self.comment = comment
        self.automatic_status = automatic_status
        self.discussion_url = discussion_url
        self.source = source

    def create_changeset(self, api):
        comment = output_full_comment_get_comment_within_limit(self.affected_objects_description, self.comment)
        changeset_description = {
            "comment": comment,
            "automatic": self.automatic_status,
            "source_code": "https://github.com/matkoniecz/OSM-wikipedia-tag-validator.git",
            "source": self.source,
            "cases_where_human_help_is_required": 'https://matkoniecz.github.io/OSM-wikipedia-tag-validator-reports/',
            }
        if self.discussion_url != None:
            changeset_description["discussion_before_edits"] = self.discussion_url
        api.ChangesetCreate(changeset_description)

def get_data(id, type):
    print("downloading", id, type)
    api = get_api(manual_username())
    try:
        if type == 'node':
            return api.NodeGet(id)
        if type == 'way':
            return api.WayGet(id)
        if type == 'relation':
            return api.RelationGet(id)
    except osmapi.ElementDeletedApiError:
        return None
    assert(False)

def update_element(api, type, data):
    if type == 'node':
        return api.NodeUpdate(data)
    if type == 'way':
        return api.WayUpdate(data)
    if type == 'relation':
        return api.RelationUpdate(data)
    assert False, str(type) + " type as not recognised"

def sleep(time_in_s):
    print("Sleeping")
    time.sleep(time_in_s)

def get_correct_api(automatic_status, discussion_url):
    if automatic_status == manually_reviewed_description():
        return get_api(manual_username())
    elif automatic_status == fully_automated_description():
        assert(discussion_url != None)
        return get_api(bot_username())
    else:
        assert(False)

def output_full_comment_get_comment_within_limit(affected_objects_description, comment):
    full_comment = affected_objects_description + " " + comment
    if(len(comment) > character_limit_of_description()):
        raise "comment too long"
    if(len(full_comment) <= character_limit_of_description()):
        comment = full_comment
    print(full_comment)
    return comment

def make_edit(affected_objects_description, comment, automatic_status, discussion_url, type, data, source, sleeping_time=60):
    api = get_correct_api(automatic_status, discussion_url)
    builder = ChangesetBuilder(affected_objects_description, comment, automatic_status, discussion_url, source)
    builder.create_changeset(api)
    update_element(api, type, data)
    api.ChangesetClose()
    if sleeping_time != 0:
        sleep(sleeping_time)

def get_and_verify_data(osm_object_url, prerequisites, failure_callback=None):
    type = osm_object_url.split("/")[3]
    id = osm_object_url.split("/")[4]
    data = get_data(id, type)
    if data == None:
        return None
    failure = prerequisite_failure_reason(osm_object_url, prerequisites, data, failure_callback)
    if failure != None:
        print(failure)
        return None
    return data

def prerequisite_failure_reason(osm_object_url, prerequisites, data, failure_callback=None):
    if failure_callback != None:
        failure_reason = failure_callback(data)
        if failure_reason != None:
            return osm_object_url + " failed with " + failure_reason

    for key in prerequisites.keys():
        if prerequisites[key] == None:
            if key in data['tag']:
                return("failed " + key + " prerequisite, as key " + key + " was present for " + osm_object_url)
        elif key not in data['tag']:
            return("failed " + key + " prerequisite, as key " + key + " was missing for " + osm_object_url)
        elif prerequisites[key] != data['tag'][key]:
            return("failed " + key + " prerequisite for " + osm_object_url)
    return None