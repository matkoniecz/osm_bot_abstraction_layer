from termcolor import colored
import re

def is_human_confirming():
    choice = input().lower()
    if choice == "y":
        return True
    return False

def list_of_address_tags():
    return ['addr:city', 'addr:town', 'addr:place', 'addr:street', 'addr:housenumber', 'addr:postcode']

def is_shop(tags):
    # list from https://github.com/gravitystorm/openstreetmap-carto/blob/master/project.mml#L1485
    if tags.get('shop') in ['supermarket', 'bag', 'bakery', 'beauty', 'bed',
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
                'music', 'medical_supply', 'dairy', 'video_games']:
        return True
    return False

def is_settlement(tags):
    if tags.get('place') in ['hamlet', 'town', 'city']:
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

def is_expected_tag(key, value, tags, special_expected):
    if special_expected.get(key) == value:
        return True
    if is_shop(tags):
        if key in ['opening_hours', 'website']:
            return True
        if key in list_of_address_tags():
            return True
    if is_settlement(tags):
        if key in ['place', 'population', 'postal_code', 'name', 'loc_name', 'alt_name']:
            return True
        for lang in all_iso_639_1_language_codes():
            if "name:" + lang == key:
                return True
    if key in ["ele"]:
        return True
    sourced_tag = re.match('source:(.*)', key)
    if sourced_tag != None:
        sourced_tag = sourced_tag.group(1)
    if sourced_tag != None:
        if tags.get(sourced_tag) != None:
            return True
    return False

def smart_print_tag_dictionary(tags, special_expected):
    for key, value in tags.items():
        text = key + "=" + value
        if is_expected_tag(key, value, tags, special_expected):
            print(text)
        else:
            print(colored(text, 'yellow'))

