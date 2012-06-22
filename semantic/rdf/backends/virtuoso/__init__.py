#-*- coding:utf-8 -*-
from django.conf import settings

from SPARQLWrapper import SPARQLWrapper, JSON

# class DatabaseFeatures(BaseDatabaseFeatures):
#     pass


# class DatabaseOperations(BaseDatabaseOperations):
#     pass


class VirtuosoConnection(object):
    """
    VirtuosoConnection class provide a simple http driver to run virtuoso
    queries
    """

    def __init__(self):
        """
        Init connection getting url to request queries
        """
        host = settings.SEMANTIC_DATABASES['default']['HOST']
        port = settings.SEMANTIC_DATABASES['default']['PORT']
        name = settings.SEMANTIC_DATABASES['default']['NAME']

        if port:
            endpoint = 'http://%s:%s/%s' % (host, port, name)
        else:
            endpoint = 'http://%s/%s' % (host, port, name)

        self.sparql = SPARQLWrapper(endpoint)

    def query(self, query):
        """
        Run a query in virtuoso

        @query: String of query that be runned

        Returns: A dictionary with the data getted by Virtuoso
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query().convert()
