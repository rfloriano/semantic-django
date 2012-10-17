import rdflib
from SPARQLWrapper import Wrapper

from django.test import TestCase


graph = rdflib.Graph()


def mocked_query(self):
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


def mocked_convert(self):
    return self.response


class SemanticTestCase(TestCase):
    def _fixture_setup(self):
        self.originalSPARQLWrapper = Wrapper.SPARQLWrapper
        Wrapper.SPARQLWrapper.query = mocked_query
        self.originalQueryResult = Wrapper.QueryResult
        Wrapper.QueryResult.convert = mocked_convert

        if hasattr(self, 'fixtures'):
            for fixture in self.fixtures:
                graph.parse(fixture, format="n3")

    def _fixture_teardown(self):
        Wrapper.SPARQLWrapper = self.originalSPARQLWrapper
        Wrapper.QueryResult = self.originalQueryResult
