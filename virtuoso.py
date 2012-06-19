from semantic.driver.virtuoso_connection import VirtuosoConnection
from semantic.interface.virtuoso_interface import VirtuosoInterface


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
