import unittest
import osm_bot_abstraction_layer.human_verification_mode as human_verification_mode

class Tests(unittest.TestCase):
    def test_empty(self):
        pass

    def test_nonsense_is_not_considered_as_valid_tag(self):
        human_verification_mode.is_expected_tag("key", "value", {"key": "value"}, {})

if __name__ == '__main__':
    unittest.main()