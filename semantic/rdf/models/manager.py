from django.db import models

from semantic.rdf.models.query import SemanticQuerySet
from semantic.rdf.models.query import SemanticEmptyQuerySet


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
