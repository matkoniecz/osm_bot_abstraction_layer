import unittest
import osm_bot_abstraction_layer.overpass_query_maker as overpass_query_maker
import datetime

class Tests(unittest.TestCase):
    def test_empty(self):
        overpass_query_maker.datetime_to_overpass_date_format(datetime.datetime.now())

