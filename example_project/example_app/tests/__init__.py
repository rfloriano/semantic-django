from django.test import TestCase

from example_app.smodels import BasePrograma


class TestBasePrograma(TestCase):
    def test_filter_from_uri(self):
        programas = BasePrograma.objects.filter(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        expected_query = "SELECT ?uri ?label ?foto_perfil ?id_do_programa_na_webmedia ?faz_parte_do_canal ?tem_edicao_do_programa FROM <http://semantica.globo.com/> WHERE { ?uri rdf:type <http://semantica.globo.com/base/Programa> ; rdfs:label ?label ; base:id_do_programa_na_webmedia ?id_do_programa_na_webmedia ; base:faz_parte_do_canal ?faz_parte_do_canal OPTIONAL { ?uri base:foto_perfil ?foto_perfil } OPTIONAL { ?uri base:tem_edicao_do_programa ?tem_edicao_do_programa } FILTER(?uri = <http://semantica.globo.com/base/Programa_Rock_in_Rio> ) }"
        self.assertEqual(programas.query.__str__(), expected_query)

    def test_get_from_uri(self):
        rock_in_rio = BasePrograma.objects.get(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(rock_in_rio.faz_parte_do_canal, u'http://semantica.globo.com/base/Canal_Multishow')
        self.assertEqual(rock_in_rio.foto_perfil, '')
        self.assertEqual(rock_in_rio.id_do_programa_na_webmedia, u'5116')
        self.assertEqual(rock_in_rio.nome, u'Rock in Rio')
        self.assertEqual(rock_in_rio.tem_edicao_do_programa, '')
        self.assertEqual(rock_in_rio.uri, u'http://semantica.globo.com/base/Programa_Rock_in_Rio')
