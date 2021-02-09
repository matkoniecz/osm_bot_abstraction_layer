import unittest
import osm_bot_abstraction_layer.world_data as world_data

class Tests(unittest.TestCase):
    def test_voivodeship_count_in_poland(self):
        data = world_data.list_of_area_divisions("PL", 4, "/tmp/test_file_PL_4.osm")
        #print(data)
        #print(len(data))

        # for debug: is there a single object with a correct tags?
        # http://overpass-turbo.eu/s/10Ab
        # ISO tags on https://www.openstreetmap.org/relation/936128 are wrong

        self.assertEqual(len(data), 16) # https://pl.wikipedia.org/wiki/Wojew%C3%B3dztwo 
        

if __name__ == '__main__':
    unittest.main()
