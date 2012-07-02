import sys
import copy

from django.db.models.base import subclass_exception
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError
from django.db.models.loading import register_models, get_model
from django.db.models.fields.related import OneToOneField

from django.db.models.base import ModelBase, Model

from semantic.rdf.models.options import SemanticOptions

from semantic.rdf.models.fields import AutoSemanticField
from semantic.rdf.models.manager import SemanticManager


class SemanticModelBase(ModelBase):
    """
    Metaclass for all models.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        # Create the class.
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        abstract = getattr(attr_meta, 'abstract', False)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)

        if getattr(meta, 'app_label', None) is None:
            # Figure out the app_label by looking one level up.
            # For 'django.contrib.sites.models', this would be 'sites'.
            model_module = sys.modules[new_class.__module__]
            kwargs = {"app_label": model_module.__name__.split('.')[-2]}
        else:
            kwargs = {}

        new_class.add_to_class('_meta', SemanticOptions(meta, **kwargs))
        if not abstract:
            new_class.add_to_class('DoesNotExist', subclass_exception('DoesNotExist',
                    tuple(x.DoesNotExist
                            for x in parents if hasattr(x, '_meta') and not x._meta.abstract)
                                    or (ObjectDoesNotExist,), module))
            new_class.add_to_class('MultipleObjectsReturned', subclass_exception('MultipleObjectsReturned',
                    tuple(x.MultipleObjectsReturned
                            for x in parents if hasattr(x, '_meta') and not x._meta.abstract)
                                    or (MultipleObjectsReturned,), module))
            if base_meta and not base_meta.abstract:
                # Non-abstract child classes inherit some attributes from their
                # non-abstract parent (unless an ABC comes before it in the
                # method resolution order).
                if not hasattr(meta, 'ordering'):
                    new_class._meta.ordering = base_meta.ordering
                if not hasattr(meta, 'get_latest_by'):
                    new_class._meta.get_latest_by = base_meta.get_latest_by

        is_proxy = new_class._meta.proxy

        if getattr(new_class, '_default_manager', None):
            if not is_proxy:
                # Multi-table inheritance doesn't inherit default manager from
                # parents.
                new_class._default_manager = None
                new_class._base_manager = None
            else:
                # Proxy classes do inherit parent's default manager, if none is
                # set explicitly.
                new_class._default_manager = new_class._default_manager._copy_to_model(new_class)
                new_class._base_manager = new_class._base_manager._copy_to_model(new_class)

        # Bail out early if we have already created this class.
        m = get_model(new_class._meta.app_label, name, False)
        if m is not None:
            return m

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # All the fields of any type declared on this model
        new_fields = new_class._meta.local_fields + \
                     new_class._meta.local_many_to_many + \
                     new_class._meta.virtual_fields
        field_names = set([f.name for f in new_fields])

        # Basic setup for proxy models.
        if is_proxy:
            base = None
            for parent in [cls for cls in parents if hasattr(cls, '_meta')]:
                if parent._meta.abstract:
                    if parent._meta.fields:
                        raise TypeError("Abstract base class containing model fields not permitted for proxy model '%s'." % name)
                    else:
                        continue
                if base is not None:
                    raise TypeError("Proxy model '%s' has more than one non-abstract model base class." % name)
                else:
                    base = parent
            if base is None:
                    raise TypeError("Proxy model '%s' has no non-abstract model base class." % name)
            if (new_class._meta.local_fields or
                    new_class._meta.local_many_to_many):
                raise FieldError("Proxy model '%s' contains model fields." % name)
            while base._meta.proxy:
                base = base._meta.proxy_for_model
            new_class._meta.setup_proxy(base)

        # Do the appropriate setup for any model parents.
        o2o_map = dict([(f.rel.to, f) for f in new_class._meta.local_fields
                if isinstance(f, OneToOneField)])

        for base in parents:
            original_base = base
            if not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue

            parent_fields = base._meta.local_fields + base._meta.local_many_to_many
            # Check for clashes between locally declared fields and those
            # on the base classes (we cannot handle shadowed fields at the
            # moment).
            for field in parent_fields:
                if field.name in field_names:
                    raise FieldError('Local field %r in class %r clashes '
                                     'with field of similar name from '
                                     'base class %r' %
                                        (field.name, name, base.__name__))
            if not base._meta.abstract:
                # Concrete classes...
                while base._meta.proxy:
                    # Skip over a proxy class to the "real" base it proxies.
                    base = base._meta.proxy_for_model
                if base in o2o_map:
                    field = o2o_map[base]
                elif not is_proxy:
                    attr_name = '%s_ptr' % base._meta.module_name
                    field = OneToOneField(base, name=attr_name,
                            auto_created=True, parent_link=True)
                    new_class.add_to_class(attr_name, field)
                else:
                    field = None
                new_class._meta.parents[base] = field
            else:
                # .. and abstract ones.
                for field in parent_fields:
                    new_class.add_to_class(field.name, copy.deepcopy(field))

                # Pass any non-abstract parent classes onto child.
                new_class._meta.parents.update(base._meta.parents)

            # Inherit managers from the abstract base classes.
            new_class.copy_managers(base._meta.abstract_managers)

            # Proxy models inherit the non-abstract managers from their base,
            # unless they have redefined any of them.
            if is_proxy:
                new_class.copy_managers(original_base._meta.concrete_managers)

            # Inherit virtual fields (like GenericForeignKey) from the parent
            # class
            for field in base._meta.virtual_fields:
                if base._meta.abstract and field.name in field_names:
                    raise FieldError('Local field %r in class %r clashes '\
                                     'with field of similar name from '\
                                     'abstract base class %r' % \
                                        (field.name, name, base.__name__))
                new_class.add_to_class(field.name, copy.deepcopy(field))

        if abstract:
            # Abstract base models can't be instantiated and don't appear in
            # the list of models for an app. We do the final setup for them a
            # little differently from normal models.
            attr_meta.abstract = False
            new_class.Meta = attr_meta
            return new_class

        new_class._prepare()
        register_models(new_class._meta.app_label, new_class)

        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return get_model(new_class._meta.app_label, name, False)

# class SemanticModelState(object):
#     """
#     A class for storing instance state
#     """
#     def __init__(self, db=None):
#         self.db = db


class SemanticModel(Model):
    __metaclass__ = SemanticModelBase

    uri = AutoSemanticField()
    objects = SemanticManager()

    class Meta:
        abstract = True

    # def __init__(self, *args, **kwargs):
    #     # Set up the storage for instance state
    #     self._state = SemanticModelState()
