from termcolor import colored
import re

def is_human_confirming():
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
    if tags.get("amenity") in ["bank", "fuel", "cafe", "fast_food", "restaurant"]:
        return True
    if tags.get("tourism") in ["museum", "hotel"]:
        return True
    return False

def is_pharmacy(tags):
    if tags.get("amenity") in ["pharmacy"]:
        return True
    if tags.get("shop") in ["chemist"]:
        return True
    return False

def food_place_tag_listing():
    return {'amenity': ["cafe", "fast_food", "restaurant", "pub"]}

def is_food_place(tags):
    return is_any_matching_with_tag_listing(tags, food_place_tag_listing())

def doctor_tag_listing():
    return {'amenity': ["dentist", "clinic", "doctors"]}

def is_doctor(tags):
    return is_any_matching_with_tag_listing(tags, doctor_tag_listing())

def is_good_main_tag(key, value):
    if check_potential_main_key(key, value, food_place_tag_listing()):
        return True
    if check_potential_main_key(key, value, shop_tag_listing()):
        return True
    if check_potential_main_key(key, value, doctor_tag_listing()):
        return True
    if key == "building" and value in expected_building_values():
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
            'payment:cryptocurrencies', 'payment:bitcoin']

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
    'factory', 'boathouse']

def get_text_before_first_colon(text):
    parsed_link = re.match('([^:]*):(.*)', text)
    if parsed_link is None:
        return None
    return parsed_link.group(1)

def is_expected_tag(key, value, tags, special_expected):
    if special_expected.get(key) == value:
        return True
    if is_good_main_tag(key, value):
        return True
    if key in ['source']:
        return True
    if tags.get("building") in expected_building_values():
        if key == "building:levels":
            if value in [str(i) for i in range(1, 20+1)]:
                return True
        if key == "roof:levels":
            if value in ["0", "1", "2"]:
                return True
    if is_indoor_poi(tags):
        if key in ['opening_hours', 'website', 'contact:website', 'level', 'operator',
                    'brand:wikidata', 'brand:wikipedia', 'brand']:
            return True
        if key in ["opening_hours:signed", "toilets", 'wifi', 'drive_through']:
            if value in ["yes", "no"]:
                return True
        if key in ['wheelchair']:
            if value in ["yes", "no", "limited"]:
                return True
        if key in ['building']:
            if value in ["yes"]:
                return True
        if key in list_of_address_tags():
            return True
    if is_food_place(tags):
        if key in ['takeaway', 'delivery', 'diet:vegan', 'diet:vegetarian', 'diet:gluten_free']:
            if value in ["yes", "no"]:
                return True
    if is_shop(tags) or is_fuel_station(tags) or is_food_place(tags):
        if key in payment_tags():
            return True
    if is_fuel_station(tags):
        if get_text_before_first_colon(key) == "fuel":
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

    if is_settlement(tags):
        if key in name_tags():
            return True
        if key in ['place', 'population', 'postal_code', 'is_in', 'wikipedia', 'wikidata',
                    #regional - Slovakia
                   'import_ref', 'region_id', 'city_id', 'city_type',
                   #regional - Poland
                   'teryt:simc', 'teryt:updated_by',
                   ]:
            return True
        for lang in all_iso_639_1_language_codes():
            for name_tag in name_tags():
                if name_tag + ":" + lang == key:
                    return True
    if key in ["ele"]:
        return True
    if tags.get("internet_access") in ["wlan", "yes", "wifi", "wired"]:
        if key == "internet_access:fee":
            if value in ["yes", "no"]:
                return True
    sourced_tag = re.match('source:(.*)', key)
    if sourced_tag != None:
        sourced_tag = sourced_tag.group(1)
    if sourced_tag != None:
        if tags.get(sourced_tag) != None:
            return True
    return False

def smart_print_tag_dictionary(tags, special_expected={}):
    for key, value in sorted(tags.items()):
        text = key + "=" + value
        if is_expected_tag(key, value, tags, special_expected):
            print(text)
        else:
            print(colored(text, 'yellow'))

