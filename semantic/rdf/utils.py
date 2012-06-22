import os

from django.conf import settings
from django.db.utils import ConnectionDoesNotExist
from django.utils.importlib import import_module

# Define some exceptions that mirror the PEP249 interface.
# We will rethrow any backend-specific errors using these
# common wrappers


class DatabaseError(Exception):
    pass


class IntegrityError(DatabaseError):
    pass


def load_backend(backend_name):
    import ipdb; ipdb.set_trace()
    try:
        module = import_module('.base', '%s' % backend_name)
        return module
    except ImportError:
        raise DatabaseError('Could not connect by %s' % backend_name)


class ConnectionHandler(object):
    def __init__(self, databases):
        self.databases = databases
        self._connections = {}

    def ensure_defaults(self, alias):
        """
        Puts the defaults into the settings dictionary for a given connection
        where no settings is provided.
        """
        try:
            conn = self.databases[alias]
        except KeyError:
            raise ConnectionDoesNotExist("The connection %s doesn't exist" % alias)

        conn.setdefault('ENGINE', 'django.db.backends.dummy')
        if conn['ENGINE'] == 'django.db.backends.' or not conn['ENGINE']:
            conn['ENGINE'] = 'django.db.backends.dummy'
        conn.setdefault('OPTIONS', {})
        conn.setdefault('TEST_CHARSET', None)
        conn.setdefault('TEST_COLLATION', None)
        conn.setdefault('TEST_NAME', None)
        conn.setdefault('TEST_MIRROR', None)
        conn.setdefault('TIME_ZONE', settings.TIME_ZONE)
        for setting in ('NAME', 'USER', 'PASSWORD', 'HOST', 'PORT'):
            conn.setdefault(setting, '')

    def __getitem__(self, alias):
        if alias in self._connections:
            return self._connections[alias]

        self.ensure_defaults(alias)
        db = self.databases[alias]
        backend = load_backend(db['ENGINE'])
        conn = backend.DatabaseWrapper(db, alias)
        self._connections[alias] = conn
        return conn

    def __iter__(self):
        return iter(self.databases)

    def all(self):
        return [self[alias] for alias in self]
