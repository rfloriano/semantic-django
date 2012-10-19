from semantic.tests import SemanticTestCase

from example_app.smodels import BasePrograma


class TestAggregates(SemanticTestCase):
    allow_virtuoso_connection = True
    semantic_fixtures = ["example_app/fixtures/fixtures_aggregates.ttl"]

    def test_count(self):
        expected = 2
        actual = BasePrograma.objects.count()
        self.assertEquals(expected, actual)
