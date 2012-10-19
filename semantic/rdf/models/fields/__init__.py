# from django.db import models
import re
import uuid

from django.core import validators
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import *


class SemanticField(Field):
    def __init__(self, graph, *args, **kwargs):
        super(SemanticField, self).__init__(*args, **kwargs)
        self.graph = graph

    def get_db_prep_lookup(self, lookup_type, value, *args, **kwargs):
        if lookup_type in ('startswith', 'istartswith', 'endswith', 'iendswith', 'contains', 'icontains'):
            return [value]
        return super(SemanticField, self).get_db_prep_lookup(lookup_type, value, *args, **kwargs)


class CharField(SemanticField):
    description = _("String (up to %(max_length)s)")

    def __init__(self, *args, **kwargs):
        super(CharField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))

    def get_internal_type(self):
        return "CharField"

    def get_prep_value(self, value):
        if isinstance(value, basestring) or value is None:
            result = value
        else:
            result = smart_unicode(value)
        return '"%s"' % result

    def formfield(self, **kwargs):
        # Passing max_length to forms.CharField means that the value's length
        # will be validated twice. This is considered acceptable since we want
        # the value in the form field (to pass into widget for example).
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(CharField, self).formfield(**defaults)


class URLField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 200)
        verify_exists = kwargs.pop('verify_exists', True)
        CharField.__init__(self, *args, **kwargs)

        self.validators.append(validators.URLValidator(verify_exists=verify_exists))


class URIField(URLField):

    def __init__(self, *args, **kwargs):
        verify_exists = kwargs.get('verify_exists', False)
        super(URIField, self).__init__(verify_exists=verify_exists, *args, **kwargs)

    def get_prep_value(self, value):
        if value:
            return '<%s>' % value
        return '"%s"' % value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Returns field's value prepared for interacting with the database
        backend.

        Used by the default implementations of ``get_db_prep_save``and
        `get_db_prep_lookup```
        """
        if not prepared:
            value = self.get_prep_value(value)
        return value


class AutoSemanticField(URIField):
    description = _("Auto Semantic Field")

    def __init__(self, graph, verbose_name='URI', name=None, primary_key=True, verify_exists=False, **kwargs):
        super(AutoSemanticField, self).__init__(verbose_name, name, verify_exists, primary_key=primary_key, **kwargs)
        self.graph = graph

    def get_prep_value(self, value):
        if not value:
            value = '%s/%s' % (self.model._meta.graph.rstrip('/'), uuid.uuid4())
        return super(AutoSemanticField, self).get_prep_value(value)


class IntegerField(IntegerField, SemanticField):
    pass
