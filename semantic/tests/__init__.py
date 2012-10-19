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

VIRTUOSO_DIR = os.path.join(os.environ['VIRTUOSO_HOME'], "var/lib/virtuoso/db/")

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


def run_isql(cmd):
    isql_cmd = ISQL_CMD % (cmd, ISQL)
    process = subprocess.Popen(isql_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = process.communicate()
    if stderr_value:
        raise Exception(stderr_value)


def copy_ttl_to_virtuoso_dir(ttl):
    fixture_dir, fixture_file = os.path.split(ttl)
    if not os.path.exists(VIRTUOSO_DIR):
        os.makedirs(VIRTUOSO_DIR)
    shutil.copyfile(ttl, os.path.join(VIRTUOSO_DIR, fixture_file))
    return fixture_file


def remove_ttl_from_virtuoso_dir(ttl):
    ttl_path = os.path.join(VIRTUOSO_DIR, ttl)
    os.remove(ttl_path)


class SemanticTestCase(TestCase):

    allow_virtuoso_connection = False
    graph = "http://testgraph.globo.com"

    def _setup_memory(self):
        self.originalSPARQLWrapper = Wrapper.SPARQLWrapper
        Wrapper.SPARQLWrapper.query = mocked_query
        self.originalQueryResult = Wrapper.QueryResult
        Wrapper.QueryResult.convert = mocked_convert

    def _teardown_memory(self):
        Wrapper.SPARQLWrapper = self.originalSPARQLWrapper
        Wrapper.QueryResult = self.originalQueryResult

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
        upload = self._upload_fixture_to_virtuoso
        if not self.allow_virtuoso_connection:
            self._setup_memory()
            upload = self._upload_fixture_to_memory
        if hasattr(self, 'semantic_fixtures'):
            for fixture in self.semantic_fixtures:
                upload(fixture)
        super(SemanticTestCase, self)._fixture_setup()

    def _fixture_teardown(self):
        if not self.allow_virtuoso_connection:
            self._teardown_memory()
        else:
            self._delete_fixture_from_virtuoso()
        super(SemanticTestCase, self)._fixture_teardown()