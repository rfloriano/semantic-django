import unittest

from semantic.rdf.models.fields import URLField


class TestSemanticFields(unittest.TestCase):
    def setUp(self):
        self.url = URLField(graph='base')

    def test_url_field_should_have_max_lenght_by_default(self):
        self.assertTrue(self.url.max_length)

    def test_url_field_should_have_200_characters_max_lenght(self):
        self.assertEqual(200, self.url.max_length)

    def test_url_field_should_have_verify_exists_validator_true_by_default(self):
        url_validator = self.url.validators[1]
        self.assertTrue(url_validator.verify_exists)
