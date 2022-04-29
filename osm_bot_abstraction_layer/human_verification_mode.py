from termcolor import colored
import webbrowser
import re

def is_human_confirming(link):
    if link != None:
        webbrowser.open(link, new=2)
    print("y + enter to confirm, anything else to reject")
    choice = input().lower()
    if choice == "y":
        return True
    return False

def list_of_address_tags():
    return ['addr:city', 'addr:town', 'addr:place', 'addr:street',
            'addr:housenumber', 'addr:postcode', 'addr:unit', 'addr:state',
            'phone', 'contact:phone', 'addr:country', 'addr:suburb',
            'addr:neighbourhood', 'addr:district', 'contact:fax']

def shop_tag_listing():
    # list from https://github.com/gravitystorm/openstreetmap-carto/blob/master/project.mml#L1485
    return {'shop': ['supermarket', 'bag', 'bakery', 'beauty', 'bed',
                'books', 'butcher', 'clothes', 'computer', 'confectionery',
                'fashion', 'convenience', 'department_store',
                'doityourself', 'hardware', 'fishmonger', 'florist',
                'garden_centre', 'hairdresser', 'hifi', 'ice_cream',
                'car', 'car_repair', 'bicycle', 'mall', 'pet',
                'photo', 'photo_studio', 'photography', 'seafood',
                'shoes', 'alcohol', 'gift', 'furniture', 'kiosk',
                'mobile_phone', 'motorcycle', 'musical_instrument',
                'newsagent', 'optician', 'jewelry', 'jewellery',
                'electronics', 'chemist', 'toys', 'travel_agency',
                'car_parts', 'greengrocer', 'farm', 'stationery',
                'laundry', 'dry_cleaning', 'beverages', 'perfumery',
                'cosmetics', 'variety_store', 'wine', 'outdoor',
                'copyshop', 'sports', 'deli', 'tobacco', 'art',
                'tea', 'coffee', 'tyres', 'pastry', 'chocolate',
                'music', 'medical_supply', 'dairy', 'video_games']}

def is_shop(tags):
    if is_pharmacy(tags):
        return True
    return is_any_matching_with_tag_listing(tags, shop_tag_listing())

def is_tag_expected_for_recycling_place(key, value, tags):
    expected_tags = {
        # https://taginfo.openstreetmap.org/search?q=recycling%3A
        'recycling_type': {'centre', 'container'},
        'recycling:glass_bottles': {'yes'},
        'recycling:paper': {'yes'},
        'recycling:glass': {'yes'},
        'recycling:clothes': {'yes'},
        'recycling:cans': {'yes'},
        'recycling:plastic': {'yes'},
        'recycling:plastic_bottles': {'yes'},
        'recycling:plastic_packaging': {'yes'},
        'recycling:cardboard': {'yes'},
        'recycling:shoes': {'yes'},
        'recycling:batteries': {'yes'},
        'recycling:scrap_metal': {'yes'},
        'recycling:green_waste': {'yes'},
        'recycling:paper_packaging': {'yes'},
    }
    if key in expected_tags:
        if value in expected_tags.get(key):
            return True
    if key == "operator":
        if value == "Polski Czerwony Krzyż":
            if tags.get("recycling:clothes") == "yes":
                return True
    return False

def is_settlement(tags):
    if tags.get('place') in ['hamlet', 'village', 'town', 'city']:
        return True
    return False

def is_fuel_station(tags):
    if tags.get('amenity') == "fuel":
        return True
    return False

def is_indoor_poi(tags):
    if is_shop(tags):
        return True
    if is_doctor(tags):
        return True
    if is_food_place(tags):
        return True
    if is_indoor_rentable_sleeping_place(tags):
        return True
    if tags.get("amenity") in ["bank", "fuel", "post_office", "cinema", "bureau_de_change"]:
        return True
    if tags.get("tourism") in ["museum"]:
        return True
    if tags.get('office') in valid_office_values():
        return True
    return False

def is_rentable_sleeping_place(tags):
    if is_indoor_rentable_sleeping_place(tags):
        return True
    if is_outdoor_rentable_sleeping_place(tags):
        return True
    return False

def is_indoor_rentable_sleeping_place(tags):
    if is_any_matching_with_tag_listing(tags, indoor_rentable_sleeping_place_tag_listing()):
        return True
    return False

def is_outdoor_rentable_sleeping_place(tags):
    if is_any_matching_with_tag_listing(tags, outdoor_rentable_sleeping_place_tag_listing()):
        return True
    return False

def indoor_rentable_sleeping_place_tag_listing():
    return {'tourism': ["hotel", "motel", "chalet", "guest_house", "apartment", "alpine_hut"]}

def outdoor_rentable_sleeping_place_tag_listing():
    return {'tourism': ["camp_site", "caravan_site"]}

def is_pharmacy(tags):
    if tags.get("amenity") in ["pharmacy"]:
        return True
    if tags.get("shop") in ["chemist"]:
        return True
    return False

def is_plant(tags):
    if tags.get("natural") in ["tree", "hedge", "wood"]:
        return True
    if tags.get("landuse") in ["forest"]:
        return True
    return False

def is_taggable_with_taxon(tags):
    if is_plant(tags):
        return True
    if tags.get("attraction") in ["enclosure", "animal"]:
        return True
    return False

def food_place_tag_listing():
    return {'amenity': ["cafe", "fast_food", "restaurant", "pub", "ice_cream"]}

def is_food_place(tags):
    return is_any_matching_with_tag_listing(tags, food_place_tag_listing())

def doctor_tag_listing():
    return {'amenity': ["dentist", "clinic", "doctors"]}

def is_doctor(tags):
    return is_any_matching_with_tag_listing(tags, doctor_tag_listing())

def brandable_tag_listing():
    return {'amenity': ["atm", "motorcycle_rental"], 'office': valid_office_values()}

def valid_office_values():
    return ['insurance']

def is_brandable(tags):
    return is_any_matching_with_tag_listing(tags, brandable_tag_listing())

def is_good_main_tag(key, value):
    if check_potential_main_key(key, value, food_place_tag_listing()):
        return True
    if check_potential_main_key(key, value, shop_tag_listing()):
        return True
    if check_potential_main_key(key, value, doctor_tag_listing()):
        return True
    if check_potential_main_key(key, value, indoor_rentable_sleeping_place_tag_listing()):
        return True
    if check_potential_main_key(key, value, outdoor_rentable_sleeping_place_tag_listing()):
        return True
    if key == "highway" and value in road_types():
        return True
    if key == "building" and value in expected_building_values():
        return True
    if key == "building:part" and value == "yes":
        return True
    return False

def is_any_matching_with_tag_listing(tags, tag_info):
    for key, value_list in tag_info.items():
        if tags.get(key) in value_list:
            return True
    return False

def check_potential_main_key(key, value, tag_list):
    values = tag_list.get(key)
    if values != None and value in values:
        return True
    return False

def all_iso_639_1_language_codes():
    #based on https://www.loc.gov/standards/iso639-2/php/English_list.php
    return ['ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av',
            'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn', 'bh', 'bi', 'nb',
            'bs', 'br', 'bg', 'my', 'es', 'ca', 'km', 'ch', 'ce', 'ny', 'ny',
            'zh', 'za', 'cu', 'cu', 'cv', 'kw', 'co', 'cr', 'hr', 'cs', 'da',
            'dv', 'dv', 'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi',
            'nl', 'fr', 'ff', 'gd', 'gl', 'lg', 'ka', 'de', 'ki', 'el', 'kl',
            'gn', 'gu', 'ht', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'is',
            'io', 'ig', 'id', 'ia', 'ie', 'iu', 'ik', 'ga', 'it', 'ja', 'jv',
            'kl', 'kn', 'kr', 'ks', 'kk', 'ki', 'rw', 'ky', 'kv', 'kg', 'ko',
            'kj', 'ku', 'kj', 'ky', 'lo', 'la', 'lv', 'lb', 'li', 'li', 'li',
            'ln', 'lt', 'lu', 'lb', 'mk', 'mg', 'ms', 'ml', 'dv', 'mt', 'gv',
            'mi', 'mr', 'mh', 'ro', 'ro', 'mn', 'na', 'nv', 'nv', 'nd', 'nr',
            'ng', 'ne', 'nd', 'se', 'no', 'nb', 'nn', 'ii', 'ny', 'nn', 'ie',
            'oc', 'oj', 'cu', 'cu', 'cu', 'or', 'om', 'os', 'os', 'pi', 'pa',
            'ps', 'fa', 'pl', 'pt', 'pa', 'ps', 'qu', 'ro', 'rm', 'rn', 'ru',
            'sm', 'sg', 'sa', 'sc', 'gd', 'sr', 'sn', 'ii', 'sd', 'si', 'si',
            'sk', 'sl', 'so', 'st', 'nr', 'es', 'su', 'sw', 'ss', 'sv', 'tl',
            'ty', 'tg', 'ta', 'tt', 'te', 'th', 'bo', 'ti', 'to', 'ts', 'tn',
            'tr', 'tk', 'tw', 'ug', 'uk', 'ur', 'ug', 'uz', 'ca', 've', 'vi',
            'vo', 'wa', 'cy', 'fy', 'wo', 'xh', 'yi', 'yo', 'za', 'zu']

def name_tags():
    return ['name', 'loc_name', 'alt_name', 'old_name', 'reg_name']

def payment_tags():
    return ['payment:visa', 'payment:mastercard', 'payment:girocard', 'payment:coins',
            'payment:maestro', 'payment:notes', 'payment:v_pay', 'payment:debit_cards',
            'payment:cash', 'payment:credit_cards',
            'payment:visa_debit', 'payment:american_express', 'payment:amex',
            'payment:diners_club', 'payment:discover_card',
            'payment:cryptocurrencies', 'payment:bitcoin', 'payment:cheque']

def expected_building_values():
    return ['yes', 'house', 'residential', 'garage', 'apartments', 'hut',
    'detached', 'industrial', 'shed', 'roof', 'commercial', 'terrace',
    'garages', 'school', 'construction', 'retail', 'greenhouse', 'barn',
    'farm_auxiliary', 'church', 'warehouse', 'service', 'cabin', 'farm',
    'civic', 'manufacture', 'static_caravan', 'university', 'office',
    'hospital', 'house', 'bungalow', 'hangar', 'kindergarten', 'mosque',
    'storage_tank', 'dormitory', 'train_station', 'stable', 'transportation',
    'transformer_tower', 'bunker', 'houseboat', 'slurry_tank', 'silo',
    'shop', 'cowshed', 'carport', 'supermarket', 'temple', 'toilets', 'kiosk',
    'factory', 'boathouse', 'hotel']

def get_text_before_first_colon(text):
    parsed_link = re.match('([^:]*):(.*)', text)
    if parsed_link is None:
        return None
    return parsed_link.group(1)

def is_place_of_payment(tags):
    if is_shop(tags):
        return True
    if is_fuel_station(tags):
        return True
    if is_food_place(tags):
        return True
    if is_rentable_sleeping_place(tags):
        return True
    if tags.get("amenity") in ["post_office"]:
        return True
    return False

def is_tag_expected_for_indoor_poi(key, value, tags):
    if key in ['opening_hours', 'website', 'contact:website', 'level', 'operator',
                'brand:wikidata', 'brand:wikipedia', 'brand']:
        return True
    if key in ["opening_hours:signed", "toilets", 'wifi', 'drive_through']:
        if value in ["yes", "no"]:
            return True
    if is_valid_wheelchair_tag(key, value):
        return True
    if key in ['building']:
        if value in expected_building_values():
            return True
    if is_valid_address_tag(key, value, tags):
        return True
    return False

def is_valid_address_tag(key, value, tags):
    if key in list_of_address_tags():
        return True
    return False

def is_valid_wheelchair_tag(key, value):
    if key in ['wheelchair']:
        if value in ["yes", "no", "limited"]:
            return True
    return False

def is_building_or_building_part(tags):
    if tags.get("building:part") in expected_building_values():
        return True
    if tags.get("building") in expected_building_values():
        return True
    return False

def is_tag_expected_for_building_or_building_part(key, value, tags):
    if key == "building:levels":
        if value in [str(i) for i in range(1, 20+1)]:
            return True
    if key == "roof:levels":
        if value in ["0", "1", "2"]:
            return True
    if key == "roof:shape":
        # https://taginfo.openstreetmap.org/keys/roof%3Ashape#values
        if value in ["flat", "gabled", "hipped", "pyramidal", "skillion", "half-hipped"]:
            return True
    return False

def is_tag_expected_for_food_place(key, value, tags):
    if key in ['outdoor_seating', 'takeaway', 'delivery',
               'diet:vegan', 'diet:vegetarian', 'diet:gluten_free']:
        if value in ["yes", "no"]:
            return True
    return False

def is_acceptable_source_tag(key, value, tags):
    sourced_tag = re.match('source:(.*)', key)
    if sourced_tag != None:
        sourced_tag = sourced_tag.group(1)
    if sourced_tag != None:
        if tags.get(sourced_tag) != None:
            return True
    return False

def unpaved_road_surfaces():
    return ["unpaved","compacted","gravel","fine_gravel","pebblestone","grass_paver",
        "ground","earth","dirt","grass","sand","mud","ice","salt","snow","woodchips"]

def paved_road_surfaces():
    return ["paved", "asphalt", "cobblestone", "cobblestone:flattened", "sett",
			"concrete", "concrete:lanes", "concrete:plates", "paving_stones",
            "metal", "wood", "unhewn_cobblestone"]

def road_types():
    return ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
		"secondary", "secondary_link", "tertiary", "tertiary_link",
		"unclassified", "residential", "living_street", "pedestrian",
        "service", "track", "road"]

def is_lit_tag_expected(tags):
    if tags.get('highway') in road_types():
        return True

def is_always_named_object(tags):
    if is_settlement(tags):
        return True
    return False

def is_frequently_named_object(tags):
    if tags.get('highway') in road_types():
        return True
    return False

def is_name_tag(key, value):
    if key in name_tags():
        return True
    for lang in all_iso_639_1_language_codes():
        for name_tag in name_tags():
            if name_tag + ":" + lang == key:
                return True
    return False

def is_expected_name_tag(key, value, tags):
    if is_always_named_object(tags) or is_frequently_named_object(tags):
        if is_name_tag(key, value):
            return True
    return False

def is_expected_tag(key, value, tags, special_expected):
    if special_expected.get(key) == value:
        return True
    if is_good_main_tag(key, value):
        return True
    if key in ['source']:
        return True
    if is_expected_name_tag(key, value, tags):
        return True
    if tags.get('highway') in road_types():
        if key == "surface":
            if value in (unpaved_road_surfaces() + paved_road_surfaces()):
                return True
        if key == "oneway" and value == "yes":
            return True
        if key == "lanes" and value == "2":
            return True
        if tags.get("oneway") == "yes" and tags.get("highway") != "motorway":
            return True
        if key == "bridge" and value in ["yes", "viaduct", "no"]:
            return True
        if key == "tunnel" and value in ["yes", "no"]:
            return True
    if key == "construction":
        if tags.get("building") == "construction":
            if value in expected_building_values():
                if value != "construction":
                    return True
        if tags.get("highway") == "construction":
            if value in road_types():
                if value != "construction":
                    return True
    if is_lit_tag_expected(tags):
        if key == "lit":
            if value in ["yes", "no"]:
                return True
    if key == "internet_access":
        if value in ["wlan", "yes", "wifi", "wired"]:
            return True
    if is_building_or_building_part(tags):
        if is_tag_expected_for_building_or_building_part(key, value, tags):
            return True
    if is_indoor_poi(tags):
        if is_tag_expected_for_indoor_poi(key, value, tags):
            return True
    if is_indoor_rentable_sleeping_place(tags):
        if key == "stars" and value in ["1", "2", "3", "4", "5"]:
            return True
    if is_outdoor_rentable_sleeping_place(tags):
        if is_valid_address_tag(key, value, tags):
            return True
    if is_food_place(tags):
        if is_tag_expected_for_food_place(key, value, tags):
            return True
    if is_place_of_payment(tags):
        if key in payment_tags():
            return True
    if tags.get('amenity') == "atm":
        if is_valid_wheelchair_tag(key, value):
            return True
        if key == "opening_hours" and value == "24/7":
            return True
        if key == "operator" and value in ["Euronet"]:
            return True
        if key == "cash_in" and value in ["yes", "no"]:
            return True
    if is_fuel_station(tags):
        if get_text_before_first_colon(key) == "fuel":
            return True
    if tags.get('attraction') in ['animal', 'enclosure']:
        if key == 'tourism' and value == 'attraction':
            return True
    if tags.get('shop') == "clothes":
        if key == 'clothes':
            return True
    if tags.get('amenity') == "bank":
        if key == 'atm':
            if value in ["yes", "no"]:
                return True
    if is_pharmacy(tags):
        if key == 'dispensing':
            if value in ["yes", "no"]:
                return True
    if is_food_place(tags):
        if key in ['cuisine', 'smoking']:
            return True
    
    if is_brandable(tags):
        if key in ['brand', 'brand:wikidata', 'brand:wikipedia']:
            return True

    if is_settlement(tags):
        if key in ['place', 'population', 'postal_code', 'is_in', 'wikipedia', 'wikidata',
                   #regional - Slovakia
                   'import_ref', 'region_id', 'city_id', 'city_type',
                   #regional - Poland
                   'teryt:simc', 'teryt:updated_by',
                   ]:
            return True
    if key in ["ele"]:
        return True
    if tags.get("internet_access") in ["wlan", "yes", "wifi", "wired"]:
        if key == "internet_access:fee":
            if value in ["yes", "no"]:
                return True
    if is_taggable_with_taxon(tags):
        if key in ["species", "species:wikidata", "species:wikipedia",
                   "genus", "genus:wikidata", "genus:wikipedia",
                   "taxon", "taxon:wikidata", "taxon:wikipedia"]:
            return True
        for language_code in all_iso_639_1_language_codes():
            if key == "species:" + language_code:
                return True
    if tags and tags.get("natural") == "tree":
        if key == "leaf_type":
            if value in ["broadleaved", "needleleaved", "palm"]:
                return True
        if key == "leaf_cycle":
            if value in ["deciduous", "evergreen", "semi_deciduous"]:
                return True
        if key == "denotation":
            # https://taginfo.openstreetmap.org/keys/denotation#values
            if value in ["natural_monument", "landmark", "urban", "avenue", "agricultural"]:
                return True
    elif is_plant(tags):
        if key == "leaf_type":
            if value in ["broadleaved", "needleleaved", "palm", "mixed"]:
                return True
        if key == "leaf_cycle":
            if value in ["deciduous", "evergreen", "semi_deciduous", "mixed"]:
                return True
    if tags.get('abandoned:man_made') == "mineshaft":
        if key in ["former_operator:wikidata", "former_operator:wikipedia"]:
            return True
    if tags.get('abandoned:man_made') == "mineshaft" or tags.get('man_made') == "mineshaft":
        if key == "resource":
            if value in ["coal"]:
                return True
    if is_acceptable_source_tag(key, value, tags):
        return True
    if tags.get("amenity") == "recycling":
        if is_tag_expected_for_recycling_place(key, value, tags):
            return True
    return False

def smart_print_tag_dictionary(tags, special_expected={}):
    for key, value in sorted(tags.items()):
        text = key + "=" + value
        if is_expected_tag(key, value, tags, special_expected):
            print(text)
        else:
            print(colored(text, 'yellow'))

