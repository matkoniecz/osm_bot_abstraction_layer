def typical_osm_timestamp_format():
    # in Overpass and in OSM Editing API timestamps
    return "%Y-%m-%dT%H:%M:%SZ"

def tag_in_wikimedia_syntax(key, value):
    if " " in key and " " in value:
        return "'" + key + "' = '" + value + "' (note presence of spaces!)"
    if " " in key:
        return "'" + key + "' = " + value + " (note presence of spaces!)"
    if " " in value:
        return key + " = '" + value + "' (note presence of spaces!)"
    for problem in ["[", "]", "{", "}", "|"]:
        if problem in key or problem in value:
            return key + "=" + value
    if "=" in key or "=" in value:
        return "{{tag|1=" + key + "|2=" + value + "}}"
    return "{{tag|" + key + "|" + value + "}}"
