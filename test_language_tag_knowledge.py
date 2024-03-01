import unittest
import osm_bot_abstraction_layer.language_tag_knowledge as language_tag_knowledge

class Tests(unittest.TestCase):
    def test_empty(self):
        pass

    def test_not_all_colon_tags_are_language_tags(self):
        self.assertEqual(False, language_tag_knowledge.is_name_key("wetap:status"))

    def test_recognizing_polish_language_tags(self):
        self.assertEqual(True, language_tag_knowledge.is_name_key("name:pl"))
        self.assertEqual(True, language_tag_knowledge.is_name_key("alt_name:pl"))
        self.assertEqual(True, language_tag_knowledge.is_name_key("loc_name:pl"))

    def test_recognizing_basic_language_tags(self):
        self.assertEqual(True, language_tag_knowledge.is_name_key("name"))

    def test_listing_basic_language_tags(self):
        self.assertEqual(True, "name" in language_tag_knowledge.name_keys())

if __name__ == '__main__':
    unittest.main()
