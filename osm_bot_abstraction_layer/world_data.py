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

def hardcoded_usa_states():
  returned = [
      {'name': 'Vermont', 'wikidata': 'Q16551'},
      {'name': 'Massachusetts', 'wikidata': 'Q771'},
      {'name': 'New York', 'wikidata': 'Q1384'},
      {'name': 'Maine', 'wikidata': 'Q724'},
      {'name': 'New Hampshire', 'wikidata': 'Q759'},
      {'name': 'Texas', 'wikidata': 'Q1439'},
      {'name': 'Illinois', 'wikidata': 'Q1204'},
      {'name': 'Missouri', 'wikidata': 'Q1581'},
      {'name': 'Kansas', 'wikidata': 'Q1558'},
      {'name': 'Oklahoma', 'wikidata': 'Q1649'},
      {'name': 'Arkansas', 'wikidata': 'Q1612'},
      {'name': 'Nebraska', 'wikidata': 'Q1553'},
      {'name': 'Iowa', 'wikidata': 'Q1546'},
      {'name': 'South Dakota', 'wikidata': 'Q1211'},
      {'name': 'North Dakota', 'wikidata': 'Q1207'},
      {'name': 'Kentucky', 'wikidata': 'Q1603'},
      {'name': 'Indiana', 'wikidata': 'Q1415'},
      {'name': 'Tennessee', 'wikidata': 'Q1509'},
      {'name': 'Mississippi', 'wikidata': 'Q1494'},
      {'name': 'Alabama', 'wikidata': 'Q173'},
      {'name': 'Georgia', 'wikidata': 'Q1428'},
      {'name': 'Colorado', 'wikidata': 'Q1261'},
      {'name': 'Wyoming', 'wikidata': 'Q1214'},
      {'name': 'Utah', 'wikidata': 'Q829'},
      {'name': 'New Mexico', 'wikidata': 'Q1522'},
      {'name': 'Arizona', 'wikidata': 'Q816'},
      {'name': 'Florida', 'wikidata': 'Q812'},
      {'name': 'Ohio', 'wikidata': 'Q1397'},
      {'name': 'West Virginia', 'wikidata': 'Q1371'},
      {'name': 'District of Columbia', 'wikidata': 'Q3551781'},
      {'name': 'Pennsylvania', 'wikidata': 'Q1400'},
      {'name': 'Delaware', 'wikidata': 'Q1393'},
      {'name': 'Maryland', 'wikidata': 'Q1391'},
      {'name': 'Montana', 'wikidata': 'Q1212'},
      {'name': 'Idaho', 'wikidata': 'Q1221'},
      {'name': 'Wisconsin', 'wikidata': 'Q1537'},
      {'name': 'Minnesota', 'wikidata': 'Q1527'},
      {'name': 'Nevada', 'wikidata': 'Q1227'},
      {'name': 'California', 'wikidata': 'Q99'},
      {'name': 'Oregon', 'wikidata': 'Q824'},
      {'name': 'Washington', 'wikidata': 'Q1223'},
      {'name': 'Michigan', 'wikidata': 'Q1166'},
      {'name': 'Connecticut', 'wikidata': 'Q779'},
      {'name': 'Hawaii', 'wikidata': 'Q782'},
      {'name': 'South Carolina', 'wikidata': 'Q1456'},
      {'name': 'Virginia', 'wikidata': 'Q1370'},
      {'name': 'North Carolina', 'wikidata': 'Q1454'},
      {'name': 'Louisiana', 'wikidata': 'Q1588'},
      {'name': 'New Jersey', 'wikidata': 'Q1408'},
      {'name': 'United States Virgin Islands', 'wikidata': 'Q11703'},
      {'name': 'Guam', 'wikidata': 'Q16635'},
      {'name': 'Northern Mariana Islands', 'wikidata': 'Q16644'},
      {'name': 'Rhode Island', 'wikidata': 'Q1387'},
      {'name': 'Alaska', 'wikidata': 'Q797'},
      {'name': 'American Samoa', 'wikidata': 'Q16641'},
      {'name': 'Puerto Rico', 'wikidata': 'Q1183'},
  ]
  random.shuffle(returned)
  return returned
