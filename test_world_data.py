import unittest
import osm_bot_abstraction_layer.world_data as world_data

class Tests(unittest.TestCase):
    def test_voivodeship_count_in_poland(self):
        data = world_data.list_of_area_divisions_data("PL", 4, "name", "/tmp/test_file_PL_4.osm")
        #print(data)
        if len(data) != 16:
            print(world_data.list_of_area_divisions_query("ISO3166-1", "PL", 4))

        # for debug: is there a single object with a correct tags?
        # http://overpass-turbo.eu/s/10Ab

        self.assertEqual(len(data), 16) # https://pl.wikipedia.org/wiki/Wojew%C3%B3dztwo 
        

if __name__ == '__main__':
    unittest.main()
