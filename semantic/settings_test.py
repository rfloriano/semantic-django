# A fake settings to compatible tests with django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'relational.db',
    }
}

SEMANTIC_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'semantic.db',
    }
}

TEST_SEMANTIC_GRAPH = "http://testgraph.globo.com"
