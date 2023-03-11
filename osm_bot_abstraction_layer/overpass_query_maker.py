import osm_bot_abstraction_layer.utils as utils

def datetime_to_overpass_data_format(datetime_data):
    return datetime_data.strftime(utils.typical_osm_timestamp_format())
