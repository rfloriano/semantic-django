from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.db.models.fields import *


class AutoSemanticField(models.URLField):
    description = _("Auto Semantic Field")

    def __init__(self, graph, verbose_name='URI', name=None, primary_key=True, verify_exists=False, **kwargs):
        super(AutoSemanticField, self).__init__(verbose_name, name, verify_exists, primary_key=primary_key, **kwargs)
        self.graph = graph


class URIField(models.URLField):
    description = _("URIField")

    def __init__(self, *args, **kwargs):
        graph = ''
        if 'graph' in kwargs:
            graph = kwargs.pop('graph')
        super(URIField, self).__init__(*args, **kwargs)
        self.graph = graph


class LiteralField(models.CharField):
    def __init__(self, graph, max_length=200, *args, **kwargs):
        self.graph = graph
        super(LiteralField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))


class IntegerField(models.IntegerField):
    def __init__(self, graph, *args, **kwargs):
        self.graph = graph
        super(IntegerField, self).__init__(*args, **kwargs)
