from semantic.tests import SemanticTestCase

from example_project.example_app.smodels import BasePrograma


class TestBaseProgramaVirtuoso(SemanticTestCase):
    semantic_fixtures = [
        "example_app/fixtures/fixture_base_programa.ttl",
        "example_app/fixtures/fixture_base_programa_to_virtuoso_access.ttl"
    ]
    allow_virtuoso_connection = True

    # def test_filter_from_uri_with_exact(self):
    #     programas = BasePrograma.objects.filter(uri='http://semantica.globo.com/base/Programa_OneProgram')
    #     self.assertEqual(len(programas), 1)
