from django.db.models.query import QuerySet, EmptyQuerySet

from semantic.rdf.models import sparql


class SemanticQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None):
        super(SemanticQuerySet, self).__init__(model, query, using)
        self.query = query or sparql.SparqlQuery(self.model)


class SemanticEmptyQuerySet(EmptyQuerySet):
    pass
