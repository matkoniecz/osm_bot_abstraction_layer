import osm_bot_abstraction_layer.utils as utils

def datetime_to_overpass_date_format(datetime_data):
    return datetime_data.strftime(utils.typical_osm_timestamp_format())

def escape_overpass_value(value):
    if "'" in value and '"' in value:
        raise Exception("both \" and ' in value, simple quoting impossible")
    if "'" in value:
        return '"' + value.replace("\\", "\\\\") + '"'
    return "'" + value.replace("\\", "\\\\") + "'"
