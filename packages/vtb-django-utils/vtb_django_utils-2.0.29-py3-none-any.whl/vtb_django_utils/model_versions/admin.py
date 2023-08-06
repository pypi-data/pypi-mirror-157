from django import forms
from django.contrib import admin
from django.db.models import JSONField
from django.forms import BaseModelForm
from django.utils.html import format_html

from .models import VersionModel
from .utils.consts import REL_VERSION_FIELD_END, REL_VERSION_PATTERN_FIELD_END
from .utils.models import get_all_available_major_version
from .utils.strings import int_arr_to_str
from ..utils.admin import PrettyJSONWidget
from ..utils.class_factory import class_factory
from ..utils.consts import DATETIME_SHORT_FORMAT
from ..utils.db import get_model_field_names


class VersionFormMixin(forms.ModelForm):
    """ Форма для версионных моделей """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_current_version()

    def setup_current_version(self):
        """ Собирает кверисеты для выбора версии по-умолчанию """
        # если инстанс основной модели сохранен и выбран инстанс связанной модели, то подтягиваем ее версии
        self.fields['current_version'] = forms.ChoiceField(widget=forms.Select, required=False, initial='')
        if self.instance:
            version_arr_list = self.instance.versions.values_list('version_arr', flat=True)
            all_version_patterns = get_all_available_major_version(version_arr_list)
            initial = [('', ''), ] if all_version_patterns else [('', ''), ('1', '1.X.X')]
            all_versions = [(s, s) for s in [int_arr_to_str(x) for x in version_arr_list]]
            self.fields['current_version'].choices = [*initial, *all_version_patterns, *all_versions]
        else:
            self.fields['current_version'].choices = [('', ''), ('1', '1.X.X')]


class VersionMixin(admin.ModelAdmin):
    """ Добавляет функционал версий модели в админке """
    form = VersionFormMixin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ['last_version']
        self.readonly_fields += ('last_version', 'version_create_dt', 'changed_by_user')
        self.fields = (('last_version', 'version_create_dt', 'changed_by_user'),
                       ('current_version',) if hasattr(self.model, 'current_version') else (),
                       ) + self.fields
        self.inlines = [create_version_inline_class(self.model)]

    @staticmethod
    def last_version(obj):
        return obj.last_version.version if obj.last_version else ''

    @staticmethod
    def version_create_dt(obj):
        return obj.last_version.create_dt.strftime(DATETIME_SHORT_FORMAT) if obj.last_version else ''

    @staticmethod
    def changed_by_user(obj):
        return obj.last_version.changed_by_user if obj.last_version else ''

    @staticmethod
    def is_version_changed(obj):
        return format_html(
            '''
            <div style="color: crimson">
            Текущая версия не сохранена (и не используется при запросе <span style="font-weight: bold">json</span>)
            </div>
            '''
        ) if obj.is_version_json_changed else ''


class RelModelsVersionSelectFormMixin(BaseModelForm):
    """ Работа со связанными версионными моделями """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_version()
        self.setup_version_pattern()

    def setup_version(self):
        """ Собирает кверисеты для выбора версий """
        for rel_field in self.instance.rel_versioned_fields:
            # если инстанс основной модели сохранен и выбран инстанс связанной модели, то подтягиваем ее версии
            if self.instance and (rel_field_object := getattr(self.instance, rel_field)):
                self.fields[f'{rel_field}{REL_VERSION_FIELD_END}'].queryset = rel_field_object.versions.all()
            # если нет, то пустой список
            else:
                self.fields[f'{rel_field}{REL_VERSION_FIELD_END}'].queryset = (
                    self.fields[f'{rel_field}{REL_VERSION_FIELD_END}'].queryset.none())

    def setup_version_pattern(self):
        """ Собирает кверисеты для выбора шаблонов версий """
        for rel_field in self.instance.rel_versioned_fields:
            version_pattern_name = f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}'
            self.fields[version_pattern_name] = forms.ChoiceField(widget=forms.Select, required=False, initial='')
            if self.instance:
                all_versions = []
                if rel_field_object := getattr(self.instance, rel_field):
                    all_versions = get_all_available_major_version(
                        rel_field_object.versions.values_list('version_arr', flat=True))
                initial = [('', ''), ] if all_versions else [('', ''), ('1', '1.X.X')]
                self.fields[version_pattern_name].choices = initial + all_versions
            else:
                self.fields[version_pattern_name].choices = [('', ''), ('1', '1.X.X')]


class VersionAdminForm(forms.ModelForm):
    class Meta:
        model = None
        fields = '__all__'


class VersionInline(admin.TabularInline):
    ordering = ('-version_arr',)
    extra = 1
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


def create_version_inline_class(model_class: VersionModel):
    """ Фабрика создания класса для редактирования модели версии """
    capitalize_name = model_class.__name__.capitalize()
    admin_module_name = __name__

    # create class Meta
    class_meta = class_factory(admin_module_name, 'Meta', (VersionAdminForm.Meta,), {})
    class_meta.model = model_class
    class_meta.fields = '__all__'

    # create class VersionAdminForm
    version_form_class = class_factory(admin_module_name, f'{capitalize_name}VersionAdminForm', (forms.ModelForm,))
    version_form_class.model = model_class
    version_form_class.Meta = class_meta

    # create class VersionInline
    version_inline_class = class_factory(admin_module_name, f'{capitalize_name}VersionInline', (VersionInline,))
    # noinspection PyUnresolvedReferences
    version_inline_class.model = model_class.versions.rel.related_model
    version_inline_class.form = version_form_class
    # noinspection PyTypeChecker
    version_inline_class.readonly_fields = get_model_field_names(
        version_inline_class.model, exclude=('id', 'json',))

    return version_inline_class
