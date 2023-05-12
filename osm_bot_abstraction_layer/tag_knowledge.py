import re
import osm_bot_abstraction_layer.language_tag_knowledge as language_tag_knowledge

def typical_main_keys():
    base = ["amenity", "tourism", "shop", "leisure", "office", "healthcare",
            "craft", 'emergency', "man_made", "traffic_calming", "barrier",
            "advertising", "highway", "natural", "power", "historic",
            "military", "attraction", "aeroway", "railway",
            "landuse", "boundary", "building", "building:part", "landcover",
            "waterway", "cemetery", "aerialway", "public_transport"]
    prefixes = ["", "construction:", "emergency:", "disused:", "abandoned:",
                "ruins:", "demolished:", "removed:", "razed:",  "destroyed:",
                "was:", "former:", "closed:"]
    # planned:, proposed:, historic: are invalid and should be avoided
    returned = []
    for prefix in prefixes:
        for basic in base:
            returned.append(prefix + basic)
    return returned

def list_of_address_tags():
    return ['addr:city', 'addr:town', 'addr:place', 'addr:street',
            'addr:housenumber', 'addr:postcode', 'addr:unit', 'addr:state',
            'phone', 'contact:phone', 'addr:country', 'addr:suburb',
            'addr:neighbourhood', 'addr:district', 'contact:fax']

def valid_shop_values():
    return [
            # list from https://github.com/gravitystorm/openstreetmap-carto/blob/master/project.mml#L1485
            'supermarket', 'bag', 'bakery', 'beauty', 'bed', 'books',
            'butcher', 'clothes', 'computer', 'confectionery',
            'convenience', 'department_store', 'doityourself', 'hardware',
            'fishmonger', 'florist', 'garden_centre', 'hairdresser', 'hifi',
            'ice_cream', 'car', 'car_repair', 'bicycle', 'mall', 'pet',
            'photo', 'photo_studio', 'photography', 'seafood', 'shoes',
            'alcohol', 'gift', 'furniture', 'kiosk', 'mobile_phone',
            'motorcycle', 'musical_instrument', 'newsagent', 'optician',
            'jewelry', 'jewellery', 'electronics', 'chemist', 'toys',
            'travel_agency', 'car_parts', 'greengrocer', 'farm', 'stationery',
            'laundry', 'dry_cleaning', 'beverages', 'perfumery', 'cosmetics',
            'variety_store', 'wine', 'outdoor', 'copyshop', 'sports', 'deli',
            'tobacco', 'art', 'tea', 'coffee', 'tyres', 'pastry', 'chocolate',
            'music', 'medical_supply', 'dairy', 'video_games',
        
            # https://taginfo.openstreetmap.org/taginfo/apidoc#api_4_tag_wiki_pages
            # reports that it is
            # * used more than 1000 times (last update on 2023-03-09)
            # * not shop=vacant / shop=no
            # * documented on wiki with one of following statuses:
            # - in use
            # - de facto
            # - approved
            # * has description on wiki
            # list generated with
            # https://gitlab.com/matkoniecz/osm-automation/-/blob/master/detect_unhandled_invalid_shop_values.py
            "tailor", "funeral_directors", "storage_rental", "trade", "massage",
            "interior_decoration", "outpost", "ticket", "houseware", "general",
            "paint", "pawnbroker", "charity", "bookmaker", "tattoo",
            "second_hand", "kitchen", "fabric", "wholesale", "lottery",
            "antiques", "gas", "craft", "agrarian", "e-cigarette",
            "hearing_aids", "money_lender", "baby_goods", "appliance",
            "electrical", "carpet", "motorcycle_repair", "cheese",
            "health_food", "pet_grooming", "grocery", "fishing", "locksmith",
            "nutrition_supplements", "bathroom_furnishing", "estate_agent",
            "curtain", "video", "watches", "rental", "fashion_accessories",
            "erotic", "sewing", "cannabis", "herbalist", "frame", "frozen_food",
            "lighting", "party", "tiles", "religion", "doors", "shoe_repair",
            "food", "flooring", "water", "leather", "telecommunication",
            "hairdresser_supply", "weapons", "swimming_pool", "radiotechnics",
            "country_store", "boat", "glaziery", "fireplace", "games", "repair",
            "fuel", "window_blind", "scuba_diving", "caravan", "printing",
            "pottery", "spices", "pyrotechnics", "tool_hire",

            # as above but has less than 1000 uses (last update on 2023-03-09)
            "collector", "vacuum_cleaner", "building_materials", "hunting",
            "printer_ink", "household_linen", "security", "model", "camera",
            "candles", "pasta", "water_sports", "honey", "motorcycle_parts",
            "anime", "energy", "rice", "trophy", "haberdashery", "catalogue",
            "groundskeeping", "wool", "shopping_centre", "wigs", "ski", "atv",
            "military_surplus", "hvac", "nuts", "truck", "garden_furniture",
            "brewing_supplies", "psychic", "insurance", "truck_repair", "shed",
            "power_tools", "souvenir", "golf", "pest_control", "ship_chandler",
            "scooter", "surf", "equestrian", "snack", "trailer", "tractor",
            "plant_hire", "medical", "piercing", "tools", "canoe_hire", "skate",
            "junk_yard", "motorsports", "bicycle_repair", "new_age", "hookah",
            "mobility_scooter", "dentures", "boat_repair", "bbq", "gold_buyer",
            "garden_machinery", "business_machines",
            "mobile_home", "wellness", "maps", "free_flying", "golf_cart",
            "window_tinting", "boat_parts", "stairs", "jetski", "kitchenware",
        ] + valid_shop_values_but_not_entirely_supported()

def valid_shop_values_but_not_entirely_supported():
    return [
        "mobile_equipment", # https://wiki.openstreetmap.org/wiki/Talk:Tag:shop%3Dmobile_equipment
        "jewellery", # https://wiki.openstreetmap.org/wiki/Proposed_features/Jewellery_shop
        'fashion', # https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfashion
        'boutique', # https://wiki.openstreetmap.org/wiki/Tag:shop%3Dboutique - In many places this tag is widely, but wrongly used to tag shops unrelated to clothing as in French speaking areas "boutique" is commonly part of a shop name. 
        'fishmonger', # https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfishmonger
        'printing', # https://wiki.openstreetmap.org/wiki/Tag:shop%3Dprinting
        '3d_printing', # RTFM user
    ]

def shop_tag_listing():
    return {'shop': valid_shop_values()}

def is_shop(tags):
    if is_pharmacy(tags):
        return True
    return is_any_matching_with_tag_listing(tags, shop_tag_listing())

def valid_barrier_values():
    # https://wiki.openstreetmap.org/wiki/Key:barrier?uselang=en#Values
    linear = ['cable_barrier', 'city_wall', 'ditch', 'fence', 'guard_rail']

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
    if tags.get("tourism") in ["museum", "gallery"]:
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
    if key == "highway" and value in path_types():
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

def name_keys():
    return language_tag_knowledge.name_tags()

def basic_name_keys():
    return language_tag_knowledge.basic_name_tags()
    
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

def additional_indoor_surface():
    return [
        # corridors
        "carpet", # documented at https://wiki.openstreetmap.org/wiki/Tag:surface%3Dcarpet
        "linoleum", # documented at https://wiki.openstreetmap.org/wiki/Tag:surface%3Dlinoleum

        # sport surfaces
        "decoturf", # documented at https://wiki.openstreetmap.org/wiki/Tag:surface%3Ddecoturf
        "tartan",
        "artificial_turf",
    ]


def road_surfaces():
    return unpaved_road_surfaces() + paved_road_surfaces()

def unpaved_road_surfaces():
    return ["unpaved","compacted","gravel","fine_gravel","pebblestone","grass_paver",
        "ground","earth","dirt","grass","sand","mud","ice","salt","snow","woodchips"]

def paved_road_surfaces():
    return ["paved", "asphalt", "cobblestone", "cobblestone:flattened", "sett",
			"concrete", "concrete:lanes", "concrete:plates", "paving_stones",
            "metal", "wood", "unhewn_cobblestone",
            "chipseal", # documented https://wiki.openstreetmap.org/wiki/Tag:surface%3Dchipseal
            ]

def road_types():
    return ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
		"secondary", "secondary_link", "tertiary", "tertiary_link",
		"unclassified", "residential", "living_street", "pedestrian",
        "service", "track", "bridleway", "busway", "road"]

def path_types():
    return ["path", "footway", "cycleway"]

def is_lit_tag_expected(tags):
    if tags.get('highway') in road_types():
        return True
    if tags.get('highway') in path_types():
        return True
    return False

def is_always_named_object(tags):
    if is_settlement(tags):
        return True
    return False

def is_frequently_named_object(tags):
    if tags.get('highway') in road_types():
        return True
    return False

def is_name_key(key):
    return language_tag_knowledge.is_name_key(key)

def is_expected_name_tag(key, value, tags):
    if is_always_named_object(tags) or is_frequently_named_object(tags):
        if is_name_key(key):
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
    if tags.get('highway') in road_types() or tags.get('highway') in path_types():
        if key == "surface":
            if value in road_surfaces():
                return True
        if key == "bridge" and value in ["yes", "viaduct", "no"]:
            return True
        if key == "tunnel" and value in ["yes", "no"]:
            return True
    if tags.get('highway') in road_types():
        if key == "oneway" and value == "yes":
            return True
        if key == "lanes" and value == "2":
            return True
        if tags.get("oneway") == "yes":
            return True
    if key == "construction":
        if tags.get("building") == "construction":
            if value in expected_building_values():
                if value != "construction":
                    return True
        if tags.get("highway") == "construction":
            if value in road_types() or value in path_types():
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
    if "building" in tags:
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
        for language_code in language_tag_knowledge.all_iso_639_1_language_codes():
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

