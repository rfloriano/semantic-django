from django.test import TestCase

from semantic.rdf.models.fields import CharField, URLField, URIField


class CharFieldTestCase(TestCase):
    def setUp(self):
        self.char_field = CharField(graph='base')

    def test_get_prepared_value_from_field(self):
        value = self.char_field.get_prep_value("test")

        self.assertEqual('"test"', value)

    def test_empty_value_returns_empty_value_after_preparation(self):
        """ regression test for issue #1 """

        value = self.char_field.get_prep_value('')

        self.assertEqual('', value)


class URLFieldTestCase(TestCase):
    def setUp(self):
        self.url = URLField(graph='base')

    def test_url_field_should_have_max_lenght_by_default(self):
        self.assertTrue(self.url.max_length)

    def test_url_field_should_have_200_characters_max_lenght(self):
        self.assertEqual(200, self.url.max_length)

    def test_url_field_should_have_verify_exists_validator_true_by_default(self):
        url_validator = self.url.validators[1]
        self.assertTrue(url_validator.verify_exists)

    def test_url_field_should_override_verify_exists(self):
        url = URLField(graph='base', verify_exists=False)
        url_validator = url.validators[1]
        self.assertFalse(url_validator.verify_exists)


class URIFieldTestCase(TestCase):
    def test_uri_field_should_have_verify_exists_validator_false_by_default(self):
        uri = URIField(graph='base')
        uri_validator = uri.validators[1]
        self.assertFalse(uri_validator.verify_exists)

    def test_uri_field_should_override_verify_exists(self):
        url = URLField(graph='base', verify_exists=True)
        url_validator = url.validators[1]
        self.assertTrue(url_validator.verify_exists)
