import osm_bot_abstraction_layer.overpass_downloader as overpass_downloader
from osm_iterator.osm_iterator import Data
    
class DataCollector( object ):
    def __init__( self, collected_keys ):
        self.data = []
        self.collected_keys = collected_keys

    def __call__( self, element ):
      collected = {}
      for key in self.collected_keys:
        collected[key] = element.get_tag_value(key)
      self.data.append(collected)

    def collected_data (self):
      return self.data

def list_of_area_divisions_query(iso_tag, area_iso_code, admin_level_of_split):
    return """[out:xml][timeout:3600];
  area
    ['""" + iso_tag + """'='""" + area_iso_code + """'] -> .parent_area;
  (
    relation["admin_level"=""" + str(admin_level_of_split) + """]["boundary"="administrative"](area.parent_area);
  );
  out tags;"""

def list_of_area_divisions_data(area_iso_code, admin_level_of_split, collected, temporary_storage_file):
    """returns data about subdivisions of area with specific iso code
     (for example PL for Poland), at specified aministrative level
    returns list with dictionaries with set of tags for each of subdivisions
   """
    keys_checked = ["ISO3166-1", "ISO3166-1:alpha2", "ISO3166-2"]
    for iso_tag in keys_checked:
      if "-" in area_iso_code and iso_tag in ["ISO3166-1", "ISO3166-1:alpha2"]:
        print("skipping", iso_tag, "as it is impossible to find correct match with such code")
        continue
      internal_division_query = list_of_area_divisions_query(iso_tag, area_iso_code, admin_level_of_split)
      overpass_downloader.download_overpass_query(internal_division_query, temporary_storage_file)
      osm = Data(temporary_storage_file)
      data_collector = DataCollector(collected)
      osm.iterate_over_data(data_collector)
      if data_collector.data != []:
        return data_collector.data
    raise Exception(area_iso_code + " not found, checked " + str(keys_checked) + " or it has no" + str(admin_level_of_split) + "boundary level - see https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative")

def countries_of_a_world(collected, temporary_storage_file):
    """returns data specified in collected of countries
    returns dictionary with keys of specified tags

    Note that it includes for example
    - miniareas with extreme autonomy
      - Falklands/Faroe Islands https://www.openstreetmap.org/relation/2185374 https://www.openstreetmap.org/relation/52939
    - countries disliked by some powers and with their existence denied
      - Taiwan/Western Sahara
    - tagging mistakes

    see also tag_analysis_ruby/tag_analysis.rb project
    """
    query = '[out:xml][timeout:1000];relation["admin_level"="2"][boundary=administrative][type!=multilinestring];out tags;'
    overpass_downloader.download_overpass_query(query, temporary_storage_file)
    osm = Data(temporary_storage_file)
    data_collector = DataCollector(collected)
    osm.iterate_over_data(data_collector)
    if data_collector.data != []:
      return data_collector.data
    else:
      raise
