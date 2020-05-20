import unittest
import osm_bot_abstraction_layer.human_verification_mode as human_verification_mode

class Tests(unittest.TestCase):
    def test_empty(self):
        pass

    def test_nonsense_is_not_considered_as_valid_tag(self):
        self.assertEqual(False, human_verification_mode.is_expected_tag("key", "value", {"key": "value"}, {}))

    def test_motels_may_be_in_hotel_buildings(self):
        tags = {"building": "hotel", "tourism": "motel"}
        self.assertEqual(True, human_verification_mode.is_expected_tag("building", "hotel", tags, {}))

    def test_roads_may_have_bridges(self):
        tags = {"highway": "tertiary", "bridge": "yes"}
        self.assertEqual(True, human_verification_mode.is_expected_tag("bridge", "yes", tags, {}))

    def test_roads_may_have_lit_bridges(self):
        tags = {"highway": "tertiary", "bridge": "yes", "lit": "yes"}
        self.assertEqual(True, human_verification_mode.is_expected_tag("lit", "yes", tags, {}))

if __name__ == '__main__':
    unittest.main()
