import rdflib
from rdflib import plugin

from django.test import TestCase
from SPARQLWrapper import Wrapper

from example_app.smodels import BasePrograma


def mocked_convert(self):
    return self.response


def mocked_query(self):
    graph = rdflib.Graph()
    graph.parse("example_app/tests/fixture.n3", format="n3")

    qres = graph.query(self.queryString)

    bindings_list = []
    for row in qres.bindings:
        row_dict = {}
        for key, value in row.items():
            if not value:
                continue

            row_item = {}

            if isinstance(value, rdflib.term.URIRef):
                type_ = 'uri'
            elif isinstance(value, rdflib.term.Literal):
                if hasattr(value, 'datatype') and value.datatype:
                    type_ = 'typed-literal'
                    row_item["datatype"] = value.datatype
                else:
                    type_ = 'literal'
            else:
                raise Exception('Unkown type')

            row_item["type"] = type_
            row_item["value"] = str(value)

            row_dict[str(key)] = row_item

        bindings_list.append(row_dict)

    binding_str = {
        'results': {
            'bindings': bindings_list
        }
    }
    return Wrapper.QueryResult(binding_str)


class TestBasePrograma(TestCase):
    def setUp(self):
        self.originalSPARQLWrapper = Wrapper.SPARQLWrapper
        Wrapper.SPARQLWrapper.query = mocked_query
        self.originalQueryResult = Wrapper.QueryResult
        Wrapper.QueryResult.convert = mocked_convert

    def tearDown(self):
        Wrapper.SPARQLWrapper = self.originalSPARQLWrapper
        Wrapper.QueryResult = self.originalQueryResult

    def test_filter_from_uri(self):
        programas = BasePrograma.objects.filter(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        expected_query = "SELECT ?uri ?label ?foto_perfil ?id_do_programa_na_webmedia ?faz_parte_do_canal ?tem_edicao_do_programa WHERE { ?uri rdf:type <http://semantica.globo.com/base/Programa> ; rdfs:label ?label ; base:id_do_programa_na_webmedia ?id_do_programa_na_webmedia ; base:faz_parte_do_canal ?faz_parte_do_canal OPTIONAL { ?uri base:foto_perfil ?foto_perfil } OPTIONAL { ?uri base:tem_edicao_do_programa ?tem_edicao_do_programa } FILTER(?uri = <http://semantica.globo.com/base/Programa_Rock_in_Rio> ) }"
        self.assertEqual(programas.query.__str__(), expected_query)

    def test_get_from_uri(self):
        rock_in_rio = BasePrograma.objects.get(uri='http://semantica.globo.com/base/Programa_Rock_in_Rio')
        self.assertEqual(rock_in_rio.faz_parte_do_canal, u'http://semantica.globo.com/base/Canal_Multishow')
        self.assertEqual(rock_in_rio.foto_perfil, '')
        self.assertEqual(rock_in_rio.id_do_programa_na_webmedia, u'5116')
        self.assertEqual(rock_in_rio.nome, u'Rock in Rio')
        self.assertEqual(rock_in_rio.tem_edicao_do_programa, '')
        self.assertEqual(rock_in_rio.uri, u'http://semantica.globo.com/base/Programa_Rock_in_Rio')
