import os
import shutil
import subprocess
import rdflib

from SPARQLWrapper import Wrapper
from django.test import TestCase
from django.conf import settings


db = settings.SEMANTIC_DATABASES['default']
ISQL = "isql"
ISQL_CMD = 'echo "%s" | %s'
ISQL_UP = "DB.DBA.TTLP_MT_LOCAL_FILE('%(ttl)s', '', '%(graph)s');"
ISQL_DOWN = "SPARQL CLEAR GRAPH <%(graph)s>;"
ISQL_SERVER = "select server_root();"

graph = rdflib.Graph()
allow_virtuoso_connection = False


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


def mocked_virtuoso_query(self):
    self.queryString = _insert_from_in_test_query(self.queryString)
    return Wrapper.QueryResult(self._query())


def _insert_from_in_test_query(query):
    if query.find('WHERE') > -1:
        splited_query = query.split('WHERE')
        splited_query.insert(1, 'FROM <%s> WHERE' % settings.TEST_SEMANTIC_GRAPH)
        return ' '.join(splited_query)
    return query


def mocked_convert(self):
    return self.response


def run_isql(cmd):
    isql_cmd = ISQL_CMD % (cmd, ISQL)
    process = subprocess.Popen(isql_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = process.communicate()
    if stderr_value:
        raise Exception(stderr_value)
    return stdout_value


def copy_ttl_to_virtuoso_dir(ttl):
    virtuoso_dir = run_isql(ISQL_SERVER).split('\n\n')[-2]
    fixture_dir, fixture_file = os.path.split(ttl)
    shutil.copyfile(ttl, os.path.join(virtuoso_dir, fixture_file))
    return fixture_file


def remove_ttl_from_virtuoso_dir(ttl):
    virtuoso_dir = run_isql(ISQL_SERVER).split('\n\n')[-2]
    ttl_path = os.path.join(virtuoso_dir, ttl)
    os.remove(ttl_path)


class SemanticTestCase(TestCase):
    originalSPARQLWrapper = Wrapper.SPARQLWrapper
    originalQueryResult = Wrapper.QueryResult
    originalQueryResultConver = Wrapper.QueryResult.convert

    allow_virtuoso_connection = False
    graph = settings.TEST_SEMANTIC_GRAPH

    def _setup_memory(self):
        Wrapper.SPARQLWrapper.query = mocked_query
        Wrapper.QueryResult.convert = mocked_convert

    def _teardown_memory(self):
        Wrapper.SPARQLWrapper = self.originalSPARQLWrapper
        Wrapper.QueryResult = self.originalQueryResult

    def _setup_virtuoso(self):
        # assert that the virtuoso wrapper is the original
        self._teardown_virtuoso()

        Wrapper.SPARQLWrapper.query = mocked_virtuoso_query

    def _teardown_virtuoso(self):
        Wrapper.SPARQLWrapper = self.originalSPARQLWrapper
        Wrapper.QueryResult = self.originalQueryResult
        Wrapper.QueryResult.convert = self.originalQueryResultConver

    def _upload_fixture_to_memory(self, fixture):
        graph.parse(fixture, format="n3")

    def _upload_fixture_to_virtuoso(self, fixture):
        fixture = copy_ttl_to_virtuoso_dir(fixture)
        isql_up = ISQL_UP % {"ttl": fixture, "graph": self.graph}
        run_isql(isql_up)

    def _delete_fixture_from_virtuoso(self):
        isql_down = ISQL_DOWN % {"graph": self.graph}
        run_isql(isql_down)

    def _fixture_setup(self):
        global allow_virtuoso_connection
        allow_virtuoso_connection = False

        if self.allow_virtuoso_connection:
            allow_virtuoso_connection = True
            upload = self._upload_fixture_to_virtuoso
            self._setup_virtuoso()
        else:
            self._setup_memory()
            upload = self._upload_fixture_to_memory

        if hasattr(self, 'semantic_fixtures'):
            for fixture in self.semantic_fixtures:
                upload(fixture)
        super(SemanticTestCase, self)._fixture_setup()

    def _fixture_teardown(self):
        if self.allow_virtuoso_connection:
            self._teardown_virtuoso()
            self._delete_fixture_from_virtuoso()
        else:
            self._teardown_memory()
        super(SemanticTestCase, self)._fixture_teardown()
