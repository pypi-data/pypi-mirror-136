import re
import string

from django import forms
from django.contrib.admin.filters import (AllValuesFieldListFilter,
                                          BooleanFieldListFilter,
                                          ChoicesFieldListFilter,
                                          FieldListFilter,
                                          RelatedFieldListFilter,
                                          SimpleListFilter,)
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.query_utils import Q
from django.utils.encoding import smart_str
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, get_language

from django.conf import settings


def get_attr(obj, attr, default=None):
    """Recursive get object's attribute. May use dot notation.

    """
    if '.' not in attr:
        return getattr(obj, attr, default)
    else:
        L = attr.split('.')
        return get_attr(getattr(obj, L[0], default), '.'.join(L[1:]), default)


class AllValuesComboFilter(AllValuesFieldListFilter):
    template = 'adminfilters/combobox.html'


class AllValuesRadioFilter(AllValuesFieldListFilter):
    template = 'adminfilters/fieldradio.html'


class RelatedFieldComboFilter(RelatedFieldListFilter):
    template = 'adminfilters/fieldcombobox.html'


class RelatedFieldRadioFilter(RelatedFieldListFilter):
    template = 'adminfilters/fieldradio.html'


class ChoicesFieldComboFilter(ChoicesFieldListFilter):
    template = 'adminfilters/combobox.html'


class ChoicesFieldRadioFilter(ChoicesFieldListFilter):
    template = 'adminfilters/fieldradio.html'


class BooleanRadioFilter(BooleanFieldListFilter):
    template = 'adminfilters/fieldradio.html'


class RelatedFieldCheckBoxFilter(RelatedFieldListFilter):
    template = 'adminfilters/fieldcheckbox.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.model_admin = model_admin
        super().__init__(field, request, params, model, model_admin, field_path)
        self.lookup_val = request.GET.getlist(self.lookup_kwarg, [])

    def queryset(self, request, queryset):
        filters = Q()

        for val in self.lookup_val:
            filters.add(Q(**{self.lookup_kwarg: val}), Q.OR)

        if (self.lookup_val_isnull):
            filters.add(Q(**{self.lookup_kwarg_isnull: self.lookup_val_isnull}), Q.OR)

        return queryset.filter(filters)

    def choices(self, cl):
        try:
            from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
        except ImportError:
            EMPTY_CHANGELIST_VALUE = self.model_admin.get_empty_value_display()

        uncheck_all = []
        uncheck_all.append("{}={}".format(self.lookup_kwarg_isnull, 1))
        for i in self.lookup_choices:
            uncheck_all.append("{}={}".format(self.lookup_kwarg, i[0]))

        yield {
            'selected': not len(self.lookup_val) and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
            'check_to_remove': "&".join(uncheck_all)

        }
        yield {
            'selected': self.lookup_val_isnull,
            'query_string': cl.get_query_string({self.lookup_kwarg_isnull: 1},
                                                [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('None'),
            'uncheck_to_remove': "{}=1".format(self.lookup_kwarg_isnull)
        }
        for pk_val, val in self.lookup_choices:
            yield {
                'selected': smart_str(pk_val) in self.lookup_val,
                'query_string': cl.get_query_string(
                    {
                        self.lookup_kwarg: pk_val,
                    },
                    [self.lookup_kwarg_isnull]),
                'display': val,
                'uncheck_to_remove': "{}={}".format(self.lookup_kwarg, pk_val) if pk_val else ""
            }
        if ((isinstance(self.field, ForeignObjectRel) and self.field.field.null or
             hasattr(self.field, 'rel') and self.field.null)):
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': cl.get_query_string(
                    {
                        self.lookup_kwarg_isnull: 'True',
                    },
                    [self.lookup_kwarg]),
                'uncheck_to_remove': "{}=1".format(self.lookup_kwarg_isnull),
                'display': EMPTY_CHANGELIST_VALUE,
            }


class TextFieldFilter(SimpleListFilter):
    template = 'adminfilters/text.html'
    lookup = None
    prefixes = None
    # lookup_val = 'field|filter'
    parameter_name = None

    @classmethod
    def factory(cls, lookup, title=None):
        if title is None:
            title = lookup.replace('__', '->')
        parts = lookup.split('__')
        if len(parts) == 1:
            lookup = '%s__iexact' % parts[0]
        elif len(parts) < 2:
            raise Exception(
                "lookup must contains at least two parts. ForeignKey|Field|Filter (groups|name|istartswith)")

        return type('TextFieldFilter',
                    (cls,), {'parameter_name': lookup.replace('__', '|'),
                             'lookup': lookup,
                             'title': title})

    @property
    def title(self):
        # getattr(field, 'verbose_name', field_path)
        return '--'

    def has_output(self):
        return True

    def value(self):
        return self.used_parameters.get(self.parameter_name, '')

    def queryset(self, request, queryset):
        if self.value():
            field = self.parameter_name.replace('|', '__')
            return queryset.filter(**{field: self.value()})
        return queryset

    def lookups(self, request, model_admin):
        return []

    def choices(self, changelist):
        yield {
            'selected': False,
            'query_string': changelist.get_query_string(
                {},
                [self.parameter_name, ]
            ),
            'lookup_kwarg': self.parameter_name,
            'display': _('All'),
            'value': self.value(),
        }


class MultiValueTextFieldFilter(TextFieldFilter):
    template = 'adminfilters/text_multi.html'
    separator = ","
    toggleable = False

    @classmethod
    def factory(cls, field, title=None, allow_exclude=True):
        if title is None:
            title = field.replace('__', '->')
        return type('MultiValueTextFieldFilter',
                    (cls,), {'parameter_name': field,
                             'allow_exclude': allow_exclude,
                             'title': title})

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.query_values = []
        self.operator = '+'
        self.parse_query_string()

    def id(self):
        return hash(f"{self.parameter_name}-{self.title}")

    def value(self):
        return self.used_parameters.get(self.parameter_name, '')

    def parse_query_string(self):
        raw_value = self.value()
        if raw_value:
            self.operator = raw_value[-1]
            entries = raw_value[:-1]
            self.query_values = [e.strip() for e in entries.split(self.separator) if e.strip()]

    def queryset(self, request, queryset):
        lookup = f"{self.parameter_name}__in"
        if self.query_values:
            if self.operator == '-':
                return queryset.exclude(**{lookup: self.query_values})
            else:
                return queryset.filter(**{lookup: self.query_values})
        return queryset

    def choices(self, changelist):
        values = self.separator.join(self.query_values)
        yield {
            'selected': False,
            'query_string': changelist.get_query_string(
                {},
                [self.parameter_name, ]
            ),
            'lookup_kwarg': self.parameter_name,
            'display': _('All'),
            'values': values,
            'operator': self.operator,
            'is_negated': (self.operator == '-')

        }

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = ('admin/js/vendor/select2/i18n/%s.js' % i18n_name,) if i18n_name else ()
        return forms.Media(
            js=('admin/js/vendor/jquery/jquery%s.js' % extra,
                ) + i18n_file + ('admin/js/jquery.init.js',
                                 'adminfilters/multivalue%s.js' % extra,
                                 ),
        )


class PermissionPrefixFilter(SimpleListFilter):
    title = 'Permission'
    parameter_name = 'perm'
    prefixes = (('add', 'Add'), ('change', 'Change'), ('delete', 'Delete'), ('--', 'Others'))
    lookup_val = None

    def lookups(self, request, model_admin):
        return self.prefixes

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value() == '--':
            k = [prefix for prefix, label in self.prefixes]
            query = Q()
            for el in k:
                query |= Q(codename__startswith=el)
            return queryset.exclude(query)
        else:
            return queryset.filter(codename__startswith=self.value())


ForeignKeyFieldFilter = TextFieldFilter


class NumberFilter(FieldListFilter):
    template = 'adminfilters/text.html'

    rex1 = re.compile(r'^(>=|<=|>|<|=)?([-+]?[0-9]+)$')
    rex2 = re.compile(r'(\d+),?')
    rex3 = re.compile(r'(\d+)')
    rex4 = re.compile(r'^(<>)?([-+]?[0-9]+)$')
    map = {">=": "gte",
           "<=": "lte",
           ">": "gt",
           "<": "lt",
           "=": "exact",
           "<>": "not",
           }

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = mark_safe(f'{self.title} <small>(use >,>=,<,<=, fixed, list)</small>')

    def choices(self, changelist):
        yield {
            'selected': False,
            'query_string': changelist.get_query_string(
                {},
                [self.field.name, ]
            ),
            'lookup_kwarg': self.field.name,
            'display': _('All'),
            'value': self.value(),
        }

    def value(self):
        return self.used_parameters.get(self.field.name, '')

    def expected_parameters(self):
        return [self.field.name]

    def queryset(self, request, queryset):
        if self.value():
            raw = self.value()
            m1 = self.rex1.match(raw)
            m2 = self.rex2.match(raw)
            m3 = self.rex3.match(raw)
            m4 = self.rex4.match(raw)
            if m1 and m1.groups():
                op, value = self.rex1.match(raw).groups()
                match = "%s__%s" % (self.field.name, self.map[op or '='])
                queryset = queryset.filter(**{match: value})
            elif m2 and m2.groups():
                value = raw.split(',')
                match = "%s__in" % self.field.name
                queryset = queryset.filter(**{match: value})
            elif m3 and m3.groups():
                match = "%s__exact" % self.field.name
                queryset = queryset.filter(**{match: raw})
            elif m4 and m3.groups():
                match = "%s__exact" % self.field.name
                queryset = queryset.exclude(**{match: raw})
            else:
                raise IncorrectLookupParameters()
        return queryset


# backward compatibility
MaxMinFilter = NumberFilter


class DependentFilter(RelatedFieldListFilter):
    pass
