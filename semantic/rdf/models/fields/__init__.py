from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import *


class AutoSemanticField(models.URLField):
    description = _("Auto Semantic Field")

    def __init__(self, verbose_name='URI', name=None, primary_key=True, verify_exists=False, **kwargs):
        super(AutoSemanticField, self).__init__(verbose_name, name, verify_exists, primary_key=primary_key, **kwargs)


class URIField(models.URLField):
    pass


class LiteralField(models.CharField):
    pass
