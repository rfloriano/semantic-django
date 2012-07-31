"""
Code to manage the creation and SPARQL rendering of 'where' constraints.
"""
import datetime
from itertools import repeat

from django.utils import tree
from django.db.models.fields import Field
# from django.db.models.query_utils import QueryWrapper
from datastructures import EmptyResultSet, FullResultSet

# Connection types
AND = '&&'
OR = '||'

DOT = '.'
SEMICOLON = ';'
SPACE = ' '


class EmptyShortCircuit(Exception):
    """
    Internal exception used to indicate that a "matches nothing" node should be
    added to the where-clause.
    """
    pass


class WhereNode(tree.Node):
    """
    Used to represent the SPARQL where-clause.

    The class is tied to the Query class that created it (in order to create
    the correct SPARQL).

    The children in this tree are usually either Q-like objects or lists of
    [table_alias, field_name, db_type, lookup_type, value_annotation,
    params]. However, a child could also be any class with as_sparql() and
    relabel_aliases() methods.
    """
    default = SEMICOLON

    def add_default_where(self, data):

    # def get_where_triples(self):
    #     # place this method in where.py
    #     tiple_format = '%(graph)s:%(field_name)s ?%(field_name)s'
    #     opts = self.query.model._meta
    #     uri_field = ''
    #     where = []
    #     where_optional = []
    #     for field, model in opts.get_fields_with_model():
    #         if field.primary_key:
    #             uri_field = field.name
    #         else:
    #             if field.blank:
    #                 where_optional.append(tiple_format % {
    #                     'graph': field.graph,
    #                     'field_name': field.name
    #                 })
    #             else:
    #                 where.append(tiple_format % {
    #                     'graph': field.graph,
    #                     'field_name': field.name
    #                 })
    #     where_string = '?%s ' % uri_field
    #     where_string += '; '.join(where)
    #     for optional in where_optional:
    #         where_string += ' OPTIONAL { ?%s %s }' % (uri_field, optional)

    #     return where_string, ''

        # import ipdb; ipdb.set_trace()
        default = []
        optional = []
        result_params = []
        for field, model in sorted(data, key=lambda field: field[0].blank):
            triple = Triple(field)
            if not triple.blank:
                array = default
            else:
                array = optional
            triple_string, triple_params = triple.as_sparql()
            if triple_string:
                array.append(triple_string)
                result_params.extend(triple_params)

        conn = ' %s ' % SEMICOLON
        sparql_string = conn.join(default)
        sparql_string += ' '
        conn = '%s' % SPACE
        sparql_string += conn.join(optional)
        return sparql_string, result_params

    def add(self, data, connector):
        """
        Add a node to the where-tree. If the data is a list or tuple, it is
        expected to be of the form (obj, lookup_type, value), where obj is
        a Constraint object, and is then slightly munged before being stored
        (to avoid storing any reference to field objects). Otherwise, the 'data'
        is stored unchanged and can be any class with an 'as_sparql()' method.
        """
        # (<django.db.models.sql.where.Constraint object at 0x10243c550>, 'exact', 'bla')
        # import ipdb; ipdb.set_trace()
        if not isinstance(data, (list, tuple)):
            super(WhereNode, self).add(data, connector)
            return

        obj, lookup_type, value = data
        if hasattr(value, '__iter__') and hasattr(value, 'next'):
            # Consume any generators immediately, so that we can determine
            # emptiness and transform any non-empty values correctly.
            value = list(value)

        # The "annotation" parameter is used to pass auxilliary information
        # about the value(s) to the query construction. Specifically, datetime
        # and empty values need special handling. Other types could be used
        # here in the future (using Python types is suggested for consistency).
        if isinstance(value, datetime.datetime):
            annotation = datetime.datetime
        elif hasattr(value, 'value_annotation'):
            annotation = value.value_annotation
        else:
            annotation = bool(value)

        if hasattr(obj, "prepare"):
            value = obj.prepare(lookup_type, value)
            super(WhereNode, self).add((obj, lookup_type, annotation, value),
                connector)
            return

        super(WhereNode, self).add((obj, lookup_type, annotation, value),
                connector)

    def as_sparql(self, qn, connection, fields=None):
        """
        Returns the SPARQL version of the where clause and the value to be
        substituted in. Returns None, None if this node is empty.

        If 'node' is provided, that is the root of the SPARQL generation
        (generally not needed except by the internal implementation for
        recursion).
        """

        if not self.children:
            return None, []
        result = []
        result_params = []
        empty = True
        for child in self.children:
            try:
                if hasattr(child, 'as_sparql'):
                    sparql, params = child.as_sparql(qn=qn, connection=connection)
                else:
                    # A leaf node in the tree.
                    sparql, params = self.make_atom(child, qn, connection)

            except EmptyResultSet:
                if self.connector == AND and not self.negated:
                    # We can bail out early in this particular case (only).
                    raise
                elif self.negated:
                    empty = False
                continue
            except FullResultSet:
                if self.connector == OR:
                    if self.negated:
                        empty = True
                        break
                    # We match everything. No need for any constraints.
                    return '', []
                if self.negated:
                    empty = True
                continue

            empty = False
            if sparql:
                result.append(sparql)
                result_params.extend(params)
        if empty:
            raise EmptyResultSet

        conn = ' %s ' % self.connector
        sparql_string = conn.join(result)
        if sparql_string:
            if self.negated:
                sparql_string = '!%s' % sparql_string
            elif len(self.children) != 1:
                sparql_string = '%s' % sparql_string

        default_params = []
        if fields:
            default_where, default_params = self.add_default_where(fields)
            sparql_string = default_where + ' FILTER(' + sparql_string + ')'

        default_params.extend(result_params)
        return sparql_string, default_params

    def make_atom(self, child, qn, connection):
        """
        Turn a tuple (table_alias, column_name, db_type, lookup_type,
        value_annot, params) into valid SPARQL.

        Returns the string for the SPARQL fragment and the parameters to use for
        it.
        """
        # import ipdb; ipdb.set_trace()
        lvalue, lookup_type, value_annot, params_or_value = child
        if hasattr(lvalue, 'process'):
            try:
                lvalue, params = lvalue.process(lookup_type, params_or_value, connection)
            except EmptyShortCircuit:
                raise EmptyResultSet
        else:
            params = Field().get_db_prep_lookup(lookup_type, params_or_value,
                connection=connection, prepared=True)

        if isinstance(lvalue, tuple):
            # A direct database column lookup.
            field_sparql = self.sparql_for_columns(lvalue, qn, connection)
        else:
            # A smart object with an as_sparql() method.
            field_sparql = lvalue.as_sparql(qn, connection)

        if value_annot is datetime.datetime:
            cast_sparql = connection.ops.datetime_cast_sparql()
        else:
            cast_sparql = '%s'

        if hasattr(params, 'as_sparql'):
            extra, params = params.as_sparql(qn, connection)
            cast_sparql = ''
        else:
            extra = ''

        if (len(params) == 1 and params[0] == '' and lookup_type == 'exact'
            and connection.features.interprets_empty_strings_as_nulls):
            lookup_type = 'isnull'
            value_annot = True

        if lookup_type in connection.operators:
            if lookup_type in ('iexact', 'icontains', 'istartswith', 'iendswith', 'contains', 'startswith', 'endswith'):
                format = "REGEX(%s, %%s %%s)" % (connection.ops.lookup_cast(lookup_type),)
            else:
                format = "%s %%s %%s" % (connection.ops.lookup_cast(lookup_type),)
            return (format % (field_sparql,
                              connection.operators[lookup_type] % cast_sparql,
                              extra), params)

        if lookup_type == 'in':
            if not value_annot:
                raise EmptyResultSet
            if extra:
                return ('%s IN %s' % (field_sparql, extra), params)
            max_in_list_size = connection.ops.max_in_list_size()
            if max_in_list_size and len(params) > max_in_list_size:
                # Break up the params list into an OR of manageable chunks.
                in_clause_elements = ['(']
                for offset in xrange(0, len(params), max_in_list_size):
                    if offset > 0:
                        in_clause_elements.append(' OR ')
                    in_clause_elements.append('%s IN (' % field_sparql)
                    group_size = min(len(params) - offset, max_in_list_size)
                    param_group = ', '.join(repeat('%s', group_size))
                    in_clause_elements.append(param_group)
                    in_clause_elements.append(')')
                in_clause_elements.append(')')
                return ''.join(in_clause_elements), params
            else:
                return ('%s IN (%s)' % (field_sparql,
                                        ', '.join(repeat('%s', len(params)))),
                        params)
        elif lookup_type in ('range', 'year'):
            return ('%s BETWEEN %%s and %%s' % field_sparql, params)
        elif lookup_type in ('month', 'day', 'week_day'):
            return ('%s = %%s' % connection.ops.date_extract_sparql(lookup_type, field_sparql),
                    params)
        elif lookup_type == 'isnull':
            return ('%s IS %sNULL' % (field_sparql,
                (not value_annot and 'NOT ' or '')), ())
        elif lookup_type == 'search':
            return (connection.ops.fulltext_search_sparql(field_sparql), params)
        elif lookup_type in ('regex', 'iregex'):
            return connection.ops.regex_lookup(lookup_type) % (field_sparql, cast_sparql), params

        raise TypeError('Invalid lookup_type: %r' % lookup_type)

    def sparql_for_columns(self, data, qn, connection):
        """
        Returns the SPARQL fragment used for the left-hand side of a column
        constraint (for example, the "T1.foo" portion in the clause
        "WHERE ... T1.foo = 6").
        """
        # TODO: improve this method to add a namespace to cases that the propertie exist in more than one namespace
        table_alias, name, db_type = data
        if table_alias:
            lhs = '%s.%s' % (qn(table_alias), qn(name))
        else:
            lhs = qn(name)
        return connection.ops.field_cast_sparql(db_type) % lhs

    def relabel_aliases(self, change_map, node=None):
        """
        Relabels the alias values of any children. 'change_map' is a dictionary
        mapping old (current) alias values to the new values.
        """
        if not node:
            node = self
        for pos, child in enumerate(node.children):
            if hasattr(child, 'relabel_aliases'):
                child.relabel_aliases(change_map)
            elif isinstance(child, tree.Node):
                self.relabel_aliases(change_map, child)
            elif isinstance(child, (list, tuple)):
                if isinstance(child[0], (list, tuple)):
                    elt = list(child[0])
                    if elt[0] in change_map:
                        elt[0] = change_map[elt[0]]
                        node.children[pos] = (tuple(elt),) + child[1:]
                else:
                    child[0].relabel_aliases(change_map)

                # Check if the query value also requires relabelling
                if hasattr(child[3], 'relabel_aliases'):
                    child[3].relabel_aliases(change_map)


class EverythingNode(object):
    """
    A node that matches everything.
    """

    def as_sparql(self, qn=None, connection=None):
        raise FullResultSet

    def relabel_aliases(self, change_map, node=None):
        return


class NothingNode(object):
    """
    A node that matches nothing.
    """
    def as_sparql(self, qn=None, connection=None):
        raise EmptyResultSet

    def relabel_aliases(self, change_map, node=None):
        return


class ExtraWhere(object):
    def __init__(self, sparqls, params):
        self.sparqls = sparqls
        self.params = params

    def as_sparql(self, qn=None, connection=None):
        conn = " %s " % AND
        return conn.join(self.sparqls), tuple(self.params or ())


class Constraint(object):
    """
    An object that can be passed to WhereNode.add() and knows how to
    pre-process itself prior to including in the WhereNode.
    """
    def __init__(self, alias, col, field):
        self.alias, self.col, self.field = alias, col, field

    def __getstate__(self):
        """Save the state of the Constraint for pickling.

        Fields aren't necessarily pickleable, because they can have
        callable default values. So, instead of pickling the field
        store a reference so we can restore it manually
        """
        obj_dict = self.__dict__.copy()
        if self.field:
            obj_dict['model'] = self.field.model
            obj_dict['field_name'] = self.field.name
        del obj_dict['field']
        return obj_dict

    def __setstate__(self, data):
        """Restore the constraint """
        model = data.pop('model', None)
        field_name = data.pop('field_name', None)
        self.__dict__.update(data)
        if model is not None:
            self.field = model._meta.get_field(field_name)
        else:
            self.field = None

    def prepare(self, lookup_type, value):
        if self.field:
            return self.field.get_prep_lookup(lookup_type, value)
        return value

    def process(self, lookup_type, value, connection):
        """
        Returns a tuple of data suitable for inclusion in a WhereNode
        instance.
        """
        # Because of circular imports, we need to import this here.
        from django.db.models.base import ObjectDoesNotExist
        try:
            if self.field:
                params = self.field.get_db_prep_lookup(lookup_type, value,
                    connection=connection, prepared=True)
                db_type = self.field.db_type(connection=connection)
            else:
                # This branch is used at times when we add a comparison to NULL
                # (we don't really want to waste time looking up the associated
                # field object at the calling location).
                params = Field().get_db_prep_lookup(lookup_type, value,
                    connection=connection, prepared=True)
                db_type = None
        except ObjectDoesNotExist:
            raise EmptyShortCircuit

        return (self.alias, self.col, db_type), params

    def relabel_aliases(self, change_map):
        if self.alias in change_map:
            self.alias = change_map[self.alias]


class Triple(object):
    primary_key = False
    blank = False

    def __init__(self, field):
        self.field = field
        if self.field.primary_key:
            self.primary_key = True
        if self.field.blank:
            self.blank = True

    def get_semantic_entity(self):
        graph = self.field.model._meta.graph.rstrip('/')
        node = self.field.model._meta.node

        if graph.startswith('http'):
            return '<%s/%s>' % (graph, node)
        else:
            return '%s:%s' % (graph, node)

    def as_sparql(self, qn=None, connection=None):
        triple_string = "%s:%s ?%s" % (self.field.graph, self.field.column, self.field.column)
        if self.field.primary_key:
            triple_string = "?%s %s:%s %s" % (self.field.column, 'rdf', 'type', self.get_semantic_entity())

        if self.field.blank:
            triple_string = 'OPTIONAL { ?uri %s }' % triple_string

        return triple_string, ()
