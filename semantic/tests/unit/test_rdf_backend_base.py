from django.test import TestCase

from semantic.rdf.models.fields import SemanticField
from semantic.rdf.backends.virtuoso.base import DatabaseOperations


class BaseBackendTestCase(TestCase):
    def test_quote_predicate(self):
        field = SemanticField(graph='base')
        predicate = 'test_with_sparql'

        database_operations = DatabaseOperations()
        quoted_predicate = database_operations.quote_predicate(field, predicate)

        self.assertEqual('base:test_with_sparql %s', quoted_predicate)
