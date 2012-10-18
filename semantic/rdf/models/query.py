from django.db.models.query import QuerySet, EmptyQuerySet, RawQuerySet

from semantic.rdf.models import sparql


class SemanticQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None):
        super(SemanticQuerySet, self).__init__(model, query, using)
        self.query = query or sparql.SparqlQuery(self.model)

    def _update(self, values):
        """
        A version of update that accepts field objects instead of field names.
        Used primarily for model saving and not intended for use by general
        code (it requires too much poking around at model internals to be
        useful at that level).
        """
        # Based on QuerySet._update, available at django/db/models/query
        # changes:
        # (+) new line
        # (*) changed
        # (-) removed (commented)
        assert self.query.can_filter(), \
                "Cannot update a query once a slice has been taken."
        query = self.query.clone(sparql.UpdateQuery)  # (*)
        query.add_update_fields(values)
        self._result_cache = None
        return query.get_compiler(self.db).execute_sparql(None)  #(*)
    _update.alters_data = True


class SemanticEmptyQuerySet(EmptyQuerySet):
    pass


class RawSemanticQuerySet(RawQuerySet):
    """
    Provides an iterator which converts the results of raw SQL queries into
    annotated model instances.
    """

    # TODO: improve dbapi to can use this class on object.raw("A SPARQL QUERY")

    def __init__(self, raw_query, model=None, query=None, params=None,
        translations=None, using=None):
        self.raw_query = raw_query
        self.model = model
        self._db = using
        self.query = query or sparql.RawSemanticQuery(sparql=raw_query, using=self.db, params=params)
        self.params = params or ()
        self.translations = translations or {}

    def using(self, alias):
        """
        Selects which database this Raw QuerySet should excecute it's query against.
        """
        return RawSemanticQuerySet(self.raw_query, model=self.model,
                query=self.query.clone(using=alias),
                params=self.params, translations=self.translations,
                using=alias)
