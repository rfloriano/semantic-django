from settings import *

INSTALLED_APPS += ('django_nose',)

TESTING = True
TEST_SEMANTIC_GRAPH = "http://testgraph.globo.com"

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = ['-s', '--verbosity=3']
