def typical_osm_timestamp_format():
    # in Overpass and in OSM Editing API timestamps
    return "%Y-%m-%dT%H:%M:%SZ"

def tag_in_wikimedia_syntax(key, value):
    for problem in ["[", "]", "{", "}", "|"]:
        if problem in key or problem in value:
            return key + "=" + value
    if "=" in key or "=" in value:
        return "{{tag|1=" + key + "|2=" + value + "}}"
    return "{{tag|" + key + "|" + value + "}}"
