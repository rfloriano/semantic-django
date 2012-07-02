from django.db import models

from semantic.rdf.models.query import SemanticQuerySet, SemanticEmptyQuerySet, \
    RawSemanticQuerySet


class SemanticManager(models.Manager):
    def __init__(self):
        super(SemanticManager, self).__init__()
        self._db = None

    def get_empty_query_set(self):
        return SemanticEmptyQuerySet(self.model, using=self._db)

    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        return SemanticQuerySet(self.model, using=self._db)

    def raw(self, raw_query, params=None, *args, **kwargs):
        return RawSemanticQuerySet(raw_query=raw_query, model=self.model, params=params, using=self._db, *args, **kwargs)
