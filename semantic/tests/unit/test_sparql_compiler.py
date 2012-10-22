from django.test import TestCase

from example_project.example_app.smodels import BasePrograma

from semantic.rdf import connections

from semantic.rdf.models.sparql.subqueries import InsertQuery


class SPARQLInsertCompilerTestCase(TestCase):
    def test_compile_to_sparql(self):
        using = 'default'
        query = InsertQuery(BasePrograma)
        programa = BasePrograma()
        query.insert_values([(programa._meta.get_field('uri'), 'uri'), (programa._meta.get_field('label'), 'test')])

        connection = connections[using]

        insert_compiler = connection.ops.compiler('SPARQLInsertCompiler')(query, connection, using)

        compiled_query = insert_compiler.as_sparql()

        self.assertEqual(('INSERT IN GRAPH <http://semantica.globo.com/> { uri rdfs:label %s;  rdf:type %s }', ['test', '<http://semantica.globo.com/base/Programa>']), compiled_query)
