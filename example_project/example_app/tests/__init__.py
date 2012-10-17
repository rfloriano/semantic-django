from semantic.tests import SemanticTestCase

from example_app.smodels import BasePrograma


class TestBasePrograma(SemanticTestCase):
    fixtures = ["example_app/tests/fixture.n3"]

    def test_filter_from_uri(self):
        programas = BasePrograma.objects.filter(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(len(programas), 1)

    def test_get_from_uri(self):
        rock_in_rio = BasePrograma.objects.get(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(rock_in_rio.faz_parte_do_canal, u'http://semantica.globo.com/base/Canal_Multishow')
        self.assertEqual(rock_in_rio.foto_perfil, '')
        self.assertEqual(rock_in_rio.id_do_programa_na_webmedia, u'5116')
        self.assertEqual(rock_in_rio.label, u'Rock in Rio')
        self.assertEqual(rock_in_rio.tem_edicao_do_programa, '')
        self.assertEqual(rock_in_rio.uri, u'http://semantica.globo.com/base/Programa_Rock_in_Rio')
