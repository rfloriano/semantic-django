#!/usr/bin/env python
#
# implements Python DBAPI 2.0
# see PEP 249 (http://www.python.org/dev/peps/pep-0249/)
import base64
import decimal


class Error(Exception):
    pass


class SparqlSyntaxError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line


class DatabaseError(Error):
    pass


class ProgrammingError(DatabaseError):
    def __init__(self, msg, **kwargs):
        DatabaseError.__init__(self, msg)


class Cursor(object):
    def __init__(self, connection, prefixes=''):
        self.arraysize = 100
        self.connection = connection
        self.sparql = None
        self.results = None
        self.pointer = 0
        self.prefixes = prefixes

    def __iter__(self):
        result = self.pointer and self.results[self.pointer:] or self.results
        return iter(result)

    def _desc(self):
        #(name, type_code, display_size, internal_size, precision, scale, null_ok)
        #first two are required, supply None for optional values
        if not self.results:
            return None

        if len(self.results) == 0:
            return None

        desc = []
        cols = [self.results.get_binding_name(i) for i in range(self.results.get_bindings_count())]
        for col in cols:
            desc_col = (col, literal_datatype(self.results.get_binding_value_by_name(col)), None, None, None, None, None)
            desc.append(desc_col)
        return desc

        #if no return values, or nothing executed
        return None
    description = property(_desc)

    def close(self):
        pass

    def _escape_param(self, param):
        if isinstance(param, (str, unicode)):
            return '"%s"' % param
        return unicode(param)

    def escape_params(self, parameters):
        #for dict, return dict
        if isinstance(parameters, dict):
            params = {}
            for k, v in parameters.iteritems():
                params[k] = self._escape_param(v)
            return params
        #for sequence, return tuple
        params = []
        for p in parameters:
            params.append(self._escape_param(p))
        return tuple(params)

    def execute(self, sparql, params=[]):
        params = self.escape_params(params)
        sparql = '%s %s' % (' '.join(self.prefixes), sparql)
        self.sparql = sparql
        self.connection.setQuery(sparql)
        self.results = self.connection.query().convert()["results"]["bindings"]

    def executemany(self, operation, seq_of_parameters):
        raise NotImplementedError('executemany need to implemented')

    # def next(self):
    #     row = self.fetchone()
    #     if row is None:
    #         raise StopIteration
    #     return row

    def fetchone(self):
        if self.pointer >= len(self.results):
            return None
        result = self.results[self.pointer]
        self.pointer += 1
        return _rowfactory(result)

    def fetchmany(self, size=None):
        end = self.pointer + (size or self.arraysize)
        results = self.results[self.pointer:end]
        self.pointer = min(end, len(self.results))
        return tuple([
            _rowfactory(r) for r in results
        ])

    def fetchall(self):
        if self.pointer:
            results = self.results[self.pointer:]
        else:
            results = self.results
        self.pointer = len(self.results)
        return tuple([
            _rowfactory(r) for r in results
        ])

    def dictfetchone(self):
        if not self.results:
            return None
        return self.results[0]

    def nextset(self):
        return None

    def setinputsizes(self):
        pass

    def setoutputsize(self, size, column=None):
        pass


def _rowfactory(row):
    return tuple([(key, value['value']) for key, value in row.items()])


def literal_datatype(node):
    if not node.is_literal():
        return None
    dt = node.literal_value['datatype']
    if dt:
        return unicode(dt)
    return u'http://www.w3.org/2001/XMLSchema#string'


SchemaToPython = {  # (schema->python, python->schema)  Does not validate.
    'http://www.w3.org/2001/XMLSchema#string': (unicode, unicode),
    'http://www.w3.org/2001/XMLSchema#normalizedString': (unicode, unicode),
    'http://www.w3.org/2001/XMLSchema#token': (unicode, unicode),
    'http://www.w3.org/2001/XMLSchema#language': (unicode, unicode),
    'http://www.w3.org/2001/XMLSchema#boolean': (bool, lambda i: unicode(i).lower()),
    'http://www.w3.org/2001/XMLSchema#decimal': (decimal.Decimal, unicode),
    'http://www.w3.org/2001/XMLSchema#integer': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#nonPositiveInteger': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#long': (long, unicode),
    'http://www.w3.org/2001/XMLSchema#nonNegativeInteger': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#negativeInteger': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#int': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#unsignedLong': (long, unicode),
    'http://www.w3.org/2001/XMLSchema#positiveInteger': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#short': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#unsignedInt': (long, unicode),
    'http://www.w3.org/2001/XMLSchema#byte': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#unsignedShort': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#unsignedByte': (int, unicode),
    'http://www.w3.org/2001/XMLSchema#float': (float, unicode),
    'http://www.w3.org/2001/XMLSchema#double': (float, unicode),  # doesn't do the whole range
#    duration
#    dateTime
#    time
#    date
#    gYearMonth
#    gYear
#    gMonthDay
#    gDay
#    gMonth
#    hexBinary
    'http://www.w3.org/2001/XMLSchema#base64Binary': (base64.decodestring, lambda i: base64.encodestring(i)[:-1]),
    'http://www.w3.org/2001/XMLSchema#anyURI': (str, str),
}
