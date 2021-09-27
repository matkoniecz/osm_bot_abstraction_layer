import osm_bot_abstraction_layer.overpass_downloader as overpass_downloader
from osm_iterator.osm_iterator import Data
    
class NameCollector( object ):
    def __init__( self ):
        self.names = []

    def __call__( self, element ):
      name = element.get_tag_value("name")
      if name != None:
        self.names.append(name)

    def collected_names (self):
      return self.names

def list_of_area_divisions_query(iso_tag, area_iso_code, admin_level_of_split):
    return """[out:xml][timeout:3600];
  area
    ['""" + iso_tag + """'='""" + area_iso_code + """'] -> .parent_area;
  (
    relation["admin_level"=""" + str(admin_level_of_split) + """]["boundary"="administrative"](area.parent_area);
  );
  out tags;"""

def list_of_area_divisions(area_iso_code, admin_level_of_split, temporary_storage_file):
    """returns list with names of subdivisions of area with specific iso code
    (for example PL for Poland), at specified aministrative level"""
    for iso_tag in ["ISO3166-1", "ISO3166-1:alpha2", "ISO3166-2"]:
      internal_division_query = list_of_area_divisions_query(iso_tag, area_iso_code, admin_level_of_split)
      overpass_downloader.download_overpass_query(internal_division_query, temporary_storage_file)
      osm = Data(temporary_storage_file)
      names = NameCollector()
      osm.iterate_over_data(names)
      if names.collected_names() != []:
        return names.collected_names()
    raise area_iso_code + " not found"

def countries_of_a_world(temporary_storage_file):
    """returns names of counties
    Note that it includes for example
    - miniareas with extreme autonomy
      - Falklands/Faroe Islands https://www.openstreetmap.org/relation/2185374 https://www.openstreetmap.org/relation/52939
    - countries disliked by some powers and with their existence denied
      - Taiwan/Western Sahara
    - tagging mistakes

    coordinate with tag_analysis_ruby/tag_analysis.rb project
    """
    query = '[out:xml];relation["admin_level"="2"][boundary=administrative][type!=multilinestring];out tags;'
    overpass_downloader.download_overpass_query(query, temporary_storage_file)
    osm = Data(temporary_storage_file)
    names = NameCollector()
    osm.iterate_over_data(names)
    if names.collected_names() != []:
      return names.collected_names()
    else:
      raise
