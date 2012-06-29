from django.db.backends import BaseDatabaseOperations
from django.utils.importlib import import_module


class BaseSemanticDatabaseOperations(BaseDatabaseOperations):
    compiler_module = "semantic.rdf.models.sparql.compiler"

    def compiler(self, compiler_name):
        """
        Returns the SPARQLCompiler class corresponding to the given name,
        in the namespace corresponding to the `compiler_module` attribute
        on this backend.
        """
        if self._cache is None:
            self._cache = import_module(self.compiler_module)
        return getattr(self._cache, compiler_name)
