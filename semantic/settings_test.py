# A fake settings to compatible tests with django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'relational.db',
    }
}

SEMANTIC_DATABASES = {
    'default': {
        'ENGINE': 'semantic.rdf.backends.virtuoso',
        'NAME': 'sparql',
        'USER': 'dba',
        'PASSWORD': 'dba',
        'HOST': 'localhost',
        'PORT': '8890',
        'PREFIX': {
            'base': '<http://semantica.globo.com/base/>',
            'g1': '<http://semantica.globo.com/G1/>',
        }
    }
}

TEST_SEMANTIC_GRAPH = "http://testgraph.globo.com"
