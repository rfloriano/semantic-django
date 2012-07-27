from django.db import utils
from django.db.backends import *
from django.db.backends.signals import connection_created
from django.db.backends.sqlite3.client import DatabaseClient
from django.db.backends.sqlite3.creation import DatabaseCreation
from django.db.backends.sqlite3.introspection import DatabaseIntrospection

from SPARQLWrapper import SPARQLWrapper as Database
from SPARQLWrapper import JSON

from semantic.rdf.backends import BaseSemanticDatabaseOperations
from semantic.rdf.backends.virtuoso.dbapi import Cursor


class DatabaseFeatures(BaseDatabaseFeatures):
    # SPARQLite cannot handle us only partially reading from a cursor's result set
    # and then writing the same rows to the database in another cursor. This
    # setting ensures we always read result sets fully into memory all in one
    # go.
    can_use_chunked_reads = False
    test_db_allows_multiple_connections = False
    supports_unspecified_pk = True
    supports_1000_query_parameters = False
    supports_mixed_date_datetime_comparisons = False

    def _supports_stddev(self):
        """Confirm support for STDDEV and related stats functions

        SPARQLite supports STDDEV as an extension package; so
        connection.ops.check_aggregate_support() can't unilaterally
        rule out support for STDDEV. We need to manually check
        whether the call works.
        """
        cursor = self.connection.cursor()
        cursor.execute('CREATE TABLE STDDEV_TEST (X INT)')
        try:
            cursor.execute('SELECT STDDEV(*) FROM STDDEV_TEST')
            has_support = True
        except utils.DatabaseError:
            has_support = False
        cursor.execute('DROP TABLE STDDEV_TEST')
        return has_support


class DatabaseOperations(BaseSemanticDatabaseOperations):
    def date_extract_sparql(self, lookup_type, field_name):
        # sparqlite doesn't support extract, so we fake it with the user-defined
        # function django_extract that's registered in connect(). Note that
        # single quotes are used because this is a string (and could otherwise
        # cause a collision with a field name).
        return "django_extract('%s', %s)" % (lookup_type.lower(), field_name)

    def date_interval_sparql(self, sparql, connector, timedelta):
        # It would be more straightforward if we could use the sparqlite strftime
        # function, but it does not allow for keeping six digits of fractional
        # second information, nor does it allow for formatting date and datetime
        # values differently. So instead we register our own function that
        # formats the datetime combined with the delta in a manner suitable
        # for comparisons.
        return  u'django_format_dtdelta(%s, "%s", "%d", "%d", "%d")' % (sparql,
            connector, timedelta.days, timedelta.seconds, timedelta.microseconds)

    def date_trunc_sparql(self, lookup_type, field_name):
        # sparqlite doesn't support DATE_TRUNC, so we fake it with a user-defined
        # function django_date_trunc that's registered in connect(). Note that
        # single quotes are used because this is a string (and could otherwise
        # cause a collision with a field name).
        return "django_date_trunc('%s', %s)" % (lookup_type.lower(), field_name)

    def drop_foreignkey_sparql(self):
        return ""

    def pk_default_value(self):
        return 'NULL'

    def quote_name(self, name):
        # if name.startswith('"') and name.endswith('"'):
        #     return name  # Quoting once is enough.
        # return '"%s"' % name
        return '?%s' % name

    def no_limit_value(self):
        return -1

    def sparql_flush(self, style, tables, sequences):
        # NB: The generated SPARQL below is specific to SPARQLite
        # Note: The DELETE FROM... SPARQL generated below works for SPARQLite databases
        # because constraints don't exist
        sparql = ['%s %s %s;' % \
                (style.SPARQL_KEYWORD('DELETE'),
                 style.SPARQL_KEYWORD('FROM'),
                 style.SPARQL_FIELD(self.quote_name(table))
                 ) for table in tables]
        # Note: No requirement for reset of auto-incremented indices (cf. other
        # sparql_flush() implementations). Just return SPARQL at this point
        return sparql

    def field_cast_sparql(self, db_type):
        """
        Given a column type (e.g. 'BLOB', 'VARCHAR'), returns the SQL necessary
        to cast it before using it in a WHERE statement. Note that the
        resulting string should contain a '%s' placeholder for the column being
        searched against.
        """
        return '%s'

    def year_lookup_bounds(self, value):
        first = '%s-01-01'
        second = '%s-12-31 23:59:59.999999'
        return [first % value, second % value]

    def convert_values(self, value, field):
        """SPARQLite returns floats when it should be returning decimals,
        and gets dates and datetimes wrong.
        For consistency with other backends, coerce when required.
        """
        internal_type = field.get_internal_type()
        if internal_type == 'DecimalField':
            return util.typecast_decimal(field.format_number(value))
        elif internal_type and internal_type.endswith('IntegerField') or internal_type == 'AutoField':
            return int(value)
        elif internal_type == 'DateField':
            return util.typecast_date(value)
        elif internal_type == 'DateTimeField':
            return util.typecast_timestamp(value)
        elif internal_type == 'TimeField':
            return util.typecast_time(value)

        # No field, or the field isn't known to be a decimal or integer
        return value


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'virtuoso'
    # SPARQLite requires LIKE statements to include an ESCAPE clause if the value
    # being escaped has a percent or underscore in it.
    # See http://www.sparqlite.org/lang_expr.html for an explanation.
    operators = {
        'exact': '= %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',

        'iexact': "LIKE %s ESCAPE '\\'",
        'contains': "LIKE %s ESCAPE '\\'",
        'icontains': "LIKE %s ESCAPE '\\'",
        'regex': 'REGEXP %s',
        'iregex': "REGEXP '(?i)' || %s",
        'startswith': "LIKE %s ESCAPE '\\'",
        'endswith': "LIKE %s ESCAPE '\\'",
        'istartswith': "LIKE %s ESCAPE '\\'",
        'iendswith': "LIKE %s ESCAPE '\\'",
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations()
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)
        if 'PREFIX' in self.settings_dict:
            self.prefixes = ['prefix %s: %s' % (key, value) \
                for key, value in self.settings_dict['PREFIX'].items()]
        else:
            self.prefixes = ''

    def _cursor(self):
        if self.connection is None:
            settings_dict = self.settings_dict
            if not settings_dict['NAME'] or not settings_dict['HOST']:
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured("Please fill out the database NAME and HOST in the settings module before using the database.")

            host = settings_dict['HOST']
            port = settings_dict['PORT']
            name = settings_dict['NAME']

            if port:
                endpoint = 'http://%s:%s/%s' % (host, port, name)
            else:
                endpoint = 'http://%s/%s' % (host, port, name)

            self.connection = Database(endpoint)
            self.connection.setReturnFormat(JSON)

            connection_created.send(sender=self.__class__, connection=self)
        return Cursor(self.connection, self.prefixes)

    def close(self):
        # If database is in memory, closing the connection destroys the
        # database. To prevent accidental data loss, ignore close requests on
        # an in-memory db.
        if self.settings_dict['NAME'] != ":memory:":
            BaseDatabaseWrapper.close(self)
