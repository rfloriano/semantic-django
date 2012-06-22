from django.conf import settings

from semantic.rdf.utils import ConnectionHandler
# from semantic.rdf.backends.virtuoso import Virtuoso

connections = ConnectionHandler(settings.SEMANTIC_DATABASES)
