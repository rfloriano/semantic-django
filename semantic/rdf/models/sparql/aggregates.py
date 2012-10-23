"""
Classes to represent the default SPARQL aggregate functions
"""


class AggregateField(object):
    """An internal field mockup used to identify aggregates in the
    data-conversion parts of the database backend.
    """
    def __init__(self, internal_type):
        self.internal_type = internal_type

    def get_internal_type(self):
        return self.internal_type

ordinal_aggregate_field = AggregateField('IntegerField')
computed_aggregate_field = AggregateField('FloatField')


class Aggregate(object):
    """
    Default SPARQL Aggregate.
    """
    is_ordinal = False
    is_computed = False
    sparql_template = '%(function)s(%(field)s)'

    def __init__(self, col, source=None, is_summary=False, **extra):
        """Instantiate an SPARQL aggregate

         * col is a column reference describing the subject field
           of the aggregate. It can be an alias, or a tuple describing
           a table and column name.
         * source is the underlying field or aggregate definition for
           the column reference. If the aggregate is not an ordinal or
           computed type, this reference is used to determine the coerced
           output type of the aggregate.
         * extra is a dictionary of additional data to provide for the
           aggregate definition

        Also utilizes the class variables:
         * sparql_function, the name of the SPARQL function that implements the
           aggregate.
         * sparql_template, a template string that is used to render the
           aggregate into SPARQL.
         * is_ordinal, a boolean indicating if the output of this aggregate
           is an integer (e.g., a count)
         * is_computed, a boolean indicating if this output of this aggregate
           is a computed float (e.g., an average), regardless of the input
           type.

        """
        self.col = col
        self.lookup = col
        self.source = source
        self.is_summary = is_summary
        self.extra = extra

        # Follow the chain of aggregate sources back until you find an
        # actual field, or an aggregate that forces a particular output
        # type. This type of this field will be used to coerce values
        # retrieved from the database.
        tmp = self

        while tmp and isinstance(tmp, Aggregate):
            if getattr(tmp, 'is_ordinal', False):
                tmp = ordinal_aggregate_field
            elif getattr(tmp, 'is_computed', False):
                tmp = computed_aggregate_field
            else:
                tmp = tmp.source

        self.field = tmp

        # Added for semantic_django
        self.default_alias = "%s__%s" % (self.sparql_function.lower(), self.col)
        self.name = self.__class__.__name__

    def relabel_aliases(self, change_map):
        if isinstance(self.col, (list, tuple)):
            self.col = (change_map.get(self.col[0], self.col[0]), self.col[1])

    def as_sparql(self, qn, connection):
        "Return the aggregate, rendered as SPARQL."

        if hasattr(self.col, 'as_sparql'):
            field_name = self.col.as_sparql(qn, connection)
        elif isinstance(self.col, (list, tuple)):
            field_name = qn(self.col[1])
        else:
            field_name = self.column

        params = {
            'function': self.sparql_function,
            'field': field_name
        }
        params.update(self.extra)

        return self.sparql_template % params

    # As in django.db.models.aggregates
    def add_to_query(self, query, alias, col, source, is_summary):
        """Add the aggregate to the nominated query.

        This method is used to convert the generic Aggregate definition into a
        backend-specific definition.

         * query is the backend-specific query instance to which the aggregate
           is to be added.
         * col is a column reference describing the subject field
           of the aggregate. It can be an alias, or a tuple describing
           a table and column name.
         * source is the underlying field or aggregate definition for
           the column reference. If the aggregate is not an ordinal or
           computed type, this reference is used to determine the coerced
           output type of the aggregate.
         * is_summary is a boolean that is set True if the aggregate is a
           summary value rather than an annotation.
        """
        klass = getattr(query.aggregates_module, self.name)
        aggregate = klass(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate



class Avg(Aggregate):
    is_computed = True
    sparql_function = 'AVG'

class Count(Aggregate):
    is_ordinal = True
    sparql_function = 'COUNT'
    sparql_template = '%(function)s(%(distinct)s%(field)s)'

    def __init__(self, col, distinct=False, **extra):
        super(Count, self).__init__(col, **extra)
        self.distinct = distinct and 'DISTINCT ' or ''

    def as_sparql(self, qn, connection):
        field_name = self.col

        params = {
            'function': self.sparql_function,
            'field': qn(field_name[1]) if isinstance(field_name, tuple) else field_name,
            'distinct': self.distinct
        }
        params.update(self.extra)

        return self.sparql_template % params


class Max(Aggregate):
    sparql_function = 'MAX'


class Min(Aggregate):
    sparql_function = 'MIN'


class Sum(Aggregate):
    sparql_function = 'SUM'
