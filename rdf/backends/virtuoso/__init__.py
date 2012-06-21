#-*- coding:utf-8 -*-
from django.conf import settings

from SPARQLWrapper import SPARQLWrapper, JSON

# from django.db.backends import BaseDatabaseFeatures, BaseDatabaseOperations, BaseDatabaseWrapper


# class DatabaseFeatures(BaseDatabaseFeatures):
#     pass


# class DatabaseOperations(BaseDatabaseOperations):
#     pass


# class DatabaseWrapper(BaseDatabaseWrapper):
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


class VirtuosoInterface(object):
    """
    Provide a default interface to access Virtuoso.
    """

    def select(self, query):
        raise NotImplementedError("You need to write a select method")

    def insert(self, query):
        raise NotImplementedError("You need to write a insert method")

    def update(self, query):
        raise NotImplementedError("You need to write a update method")

    def delete(self, query):
        raise NotImplementedError("You need to write a delete method")


class Virtuoso(VirtuosoInterface):
    """
    Provide the default access to Virtuoso
    """
    _connection = VirtuosoConnection()

    def select(self, query):
        return self._query(query)

    def update(self, query):
        return self._query(query)

    def delete(self, query):
        return self._query(query)

    def insert(self, query):
        return self._query(query)

    def _query(self, query):
        """
        Delegate a query and send to Virtuoso Connection
        """

        return self._connection.query(query)
