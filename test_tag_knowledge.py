import unittest
import osm_bot_abstraction_layer.tag_knowledge as tag_knowledge

class Tests(unittest.TestCase):
    def test_empty(self):
        pass

    def test_nonsense_is_not_considered_as_valid_tag(self):
        self.assertEqual(False, tag_knowledge.is_expected_tag("key", "value", {"key": "value"}, {}))

    def test_motels_may_be_in_hotel_buildings(self):
        tags = {"building": "hotel", "tourism": "motel"}
        self.assertEqual(True, tag_knowledge.is_expected_tag("building", "hotel", tags, {}))

    def test_roads_may_have_bridges(self):
        tags = {"highway": "tertiary", "bridge": "yes"}
        self.assertEqual(True, tag_knowledge.is_expected_tag("bridge", "yes", tags, {}))

    def test_roads_may_have_lit_bridges(self):
        tags = {"highway": "tertiary", "bridge": "yes", "lit": "yes"}
        self.assertEqual(True, tag_knowledge.is_expected_tag("lit", "yes", tags, {}))

    def test_main_tags_can_be_prefixed_tags(self):
        self.assertEqual(True, 'disused:amenity' in tag_knowledge.typical_main_keys())

    def test_main_tags_list_amenity_before_demolished_amenity(self):
        self.assertEqual(True, tag_knowledge.typical_main_keys().index("amenity") < tag_knowledge.typical_main_keys().index("demolished:amenity"))

    def test_road_is_not_shoplike(self):
        tags = {"highway": "tertiary"}
        self.assertEqual(False, tag_knowledge.is_shoplike(tags))

    def test_supermarket_is_shoplike(self):
        tags = {"shop": "supermarket"}
        self.assertEqual(True, tag_knowledge.is_shoplike(tags))

if __name__ == '__main__':
    unittest.main()
