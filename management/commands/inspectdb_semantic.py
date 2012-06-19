from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from semantic.virtuoso import Virtuoso


class Command(BaseCommand):
    help = "Introspects the database tables in the given database and outputs a Django model module."

    option_list = BaseCommand.option_list + (
        make_option('--graph', action='store', dest='graph',
            help='Nominates a graph to semantic introspect.'),
    )

    requires_model_validation = False

    db_module = 'g1_libs.semantic'
    virtuoso = Virtuoso()
    graph = ''

    def handle(self, **options):
        self.graph = options.get('graph', None)

        if not self.graph:
            raise CommandError("A graph need to be specified to inspection")

        self.graph = options['graph']
        if not self.graph.endswith("/"):
            self.graph += "/"

        query = """
            SELECT DISTINCT(?class) WHERE {
                {
                    ?class rdf:type <http://www.w3.org/2002/07/owl#Class>.
                    ?class rdfs:subClassOf ?parent.
                }   union {
                        ?class rdfs:comment ?comment
                }
                FILTER REGEX (?class, '%(graph)s')
            }
        """ % {"graph": self.graph}
        results = self.get_results(query)

        class_data = {}
        for result in results:
            klass = self.get_or_blank(result, 'class')
            data = self.get_data_class(klass)
            properties = self.get_class_properties(klass)

            class_data[klass] = {
                'data': data,
                'properties': properties,
            }

        for line in self.make_model(class_data):
            self.stdout.write("%s\n" % line)

    def get_or_blank(self, data, key):
        try:
            return data[key]['value']
        except KeyError:
            return ''

    def get_results(self, query):
        return self.virtuoso._query(query)['results']['bindings']

    def get_data_class(self, klass):
        query = """
            SELECT * WHERE {
                <%(class)s> rdfs:subClassOf ?parent .
                OPTIONAL { <%(class)s> rdfs:comment ?comment }
                FILTER REGEX (?parent, '%(graph)s')
            }
        """ % {'graph': self.graph, 'class': klass}
        return self.get_results(query)

    def get_parent_graph_and_parent_class(self, uri):
        parent_graph = ''
        parent_class = ''
        if self.graph in uri:
            uri = uri.replace(uri, '')
            parent_graph, parent_class = uri.split('/')
        return parent_graph, parent_class

    def get_class_properties(self, klass):
        query = """
            SELECT * WHERE {
                ?property rdfs:domain <%(class)s>
            }
        """ % {'class': klass}
        return self.get_results(query)

    def get_name_from_uri(self, uri):
        path = uri.replace(self.graph, '').strip('/')
        name = path \
            .replace('/', '') \
            .replace(' ', '') \
            .replace('_', '') \
            .replace('-', '')
        return self.capfirst(name)

    def get_field_property(self, prop):
        splited_uri = prop['value'].split('/')
        name = splited_uri.pop()
        return name, self.capfirst(prop['type'])

    def get_meta(self, graph):
        return ['    class Meta:',
                '        semantic_graph = %r' % graph,
                '']

    def get_parent(self, parent_uri):
        return self.get_name_from_uri(parent_uri)

    def capfirst(self, value):
        return value and value[0].upper() + value[1:]

    def make_model(self, data):
        yield "# This is an auto-generated Semantic Globo model module."
        yield "# You'll have to do the following manually to clean this up:"
        yield "#     * Rearrange models' order"
        yield "# Feel free to rename the models, but don't rename semantic_graph values or field names."
        yield "#"
        yield ''
        yield 'from %s import models' % self.db_module
        yield ''
        yield ''
        for graph_uri, data in data.items():
            klass_name = self.get_name_from_uri(graph_uri)

            if not klass_name:
                continue

            parent_class = 'models.SemanticModel'
            if len(data['data']) > 0 and 'parent' in data['data'][0]:
                parent_class = self.get_parent(self.get_or_blank(data['data'][0], 'parent'))

            yield 'class %s(%s):' % (klass_name, parent_class)

            if len(data['data']) > 0 and 'comment' in data['data'][0]:
                yield '    """%s"""' % self.get_or_blank(data['data'][0], 'comment')

            if not data['properties']:
                yield '    pass'
            else:
                for prop in data['properties']:
                    yield '    %s = models.%sField()' % (self.get_field_property(prop['property']))

            yield ''

            for l in self.get_meta(graph_uri):
                yield l
