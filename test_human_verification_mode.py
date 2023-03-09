import unittest
import osm_bot_abstraction_layer.human_verification_mode as human_verification_mode

class Tests(unittest.TestCase):
    def test_smart_print_tag_dictionary(self):
        human_verification_mode.smart_print_tag_dictionary({'building': 'house', 'aaa': 'nnn'})

if __name__ == '__main__':
    unittest.main()
