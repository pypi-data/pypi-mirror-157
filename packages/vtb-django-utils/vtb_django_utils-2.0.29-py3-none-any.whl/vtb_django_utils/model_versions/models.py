from __future__ import annotations

import json
import uuid
from abc import ABCMeta
from typing import Optional, List, Tuple, Type, Union

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import JSONField, Func, F, Value
from django_lifecycle import hook, BEFORE_SAVE, LifecycleModelMixin

from .utils.consts import VERSION_DELIMITER, ERR_VERSIONED_OBJ_DONT_MATCH_SELECTED_VERSION, VERSION_MODEL_SUFFIX, \
    RE_VERSION, \
    ERR_VERSION_FORMAT, \
    VERSION_PATTERN_REGEX, \
    ERR_WRONG_VERSION_PATTERN_FORMAT
from .utils.models import get_rel_versioned_field_names
from .utils.regex import version_regex
from .utils.strings import int_arr_to_str, str_to_int_arr, next_version_str
from ..user_info.info import get_user_info
from ..utils.class_factory import class_factory
from ..utils.db import CreatedMixin, get_model_field_names
from ..utils.jsons import get_json_hash, JSONEncoder


class VersionModel(CreatedMixin, models.Model):
    """ Базовый класс для версий какой-либо модели """
    user = JSONField(default=dict, blank=True)
    json = JSONField(default=dict, blank=True)
    hash = models.TextField()
    version_arr = ArrayField(models.PositiveSmallIntegerField(), max_length=3, default=list, blank=True)

    class Meta:
        abstract = True

    def patch_version(self):
        """ Позволяет изменить инстанс версии, без создания копии """
        # noinspection PyUnresolvedReferences
        self._initial_state['hash'] = get_json_hash(self.json)  # нужно чтобы новая версия не создалась
        self.save()

    def clean(self):
        super().clean()
        self._validate_version_range()

    @hook(BEFORE_SAVE)
    def _validate_version_range(self):
        self._before_save_version()

        if not RE_VERSION.match(int_arr_to_str(self.version_arr)):
            raise ValidationError(ERR_VERSION_FORMAT.format(self.version_arr))

    def _before_save_version(self):
        self.user = get_user_info()
        self.hash = get_json_hash(self.json) if self.json else ''
        if not self.version_arr:
            self.version_arr = str_to_int_arr(getattr(self, self.main_model_name.lower()).next_version_str)

        # не даем изменять версию, нужно создать новую
        # noinspection PyUnresolvedReferences
        old_hash = self.initial_value('hash')
        if self.pk and old_hash and self.hash != old_hash:
            self.pk = None
            self.version_arr = str_to_int_arr(getattr(self, self.main_model_name.lower()).next_version_str)
            self.save()
            # откатываем изменения в старой версии
            for attr in get_model_field_names(self.__class__, exclude=(self.main_model_name.lower(),)):
                # noinspection PyUnresolvedReferences
                setattr(self, attr, self.initial_value(attr))

    @property
    def version(self) -> str:
        """ Возвращает версию в виде строки """
        return int_arr_to_str(self.version_arr)

    @property
    def changed_by_user(self) -> str:
        """ Имя пользователя, создавшего версию """
        # noinspection PyUnresolvedReferences
        return self.user.get('username', '')

    @property
    def main_model_name(self):
        return getattr(self, '_main_model_name')

    @classmethod
    def get_instance_by_pattern(
            cls, rel_field_id_name: str, rel_field_id: uuid, pattern_attr: str = None) -> VersionModel:
        """ Возвращает инстанс версии модели по шаблону """
        query = cls.objects.filter(**{rel_field_id_name: rel_field_id})

        if not pattern_attr:
            version_instance = query.order_by('-version_arr').first()

        elif len([s for s in pattern_attr.split(VERSION_DELIMITER) if s]) < 3:
            # это паттерн
            version_instance = query.annotate(
                exact_version=Func(F('version_arr'), Value(VERSION_DELIMITER), function='array_to_string')
            ).filter(
                exact_version__regex=version_regex(pattern_attr)
            ).order_by('-version_arr').first()

        else:
            # это строка с версией
            try:
                version_instance = query.get(version_arr=str_to_int_arr(pattern_attr))
            except cls.DoesNotExist:
                raise ValidationError(
                    ERR_VERSIONED_OBJ_DONT_MATCH_SELECTED_VERSION.format(pattern_attr, rel_field_id_name, rel_field_id))

        if not version_instance:
            raise ValidationError(
                ERR_VERSIONED_OBJ_DONT_MATCH_SELECTED_VERSION.format(pattern_attr, rel_field_id_name, rel_field_id))

        return version_instance


class VersionedModelMixin(models.Model):
    """ Добавляет методы для работы с версиями модели """
    __metaclass__ = ABCMeta

    current_version = models.CharField(
        help_text='Версия или паттерн для выдачи объекта по-умолчанию. Если не задано, то отдается последняя версия',
        max_length=11, default='', blank=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_versioned_fields = get_rel_versioned_field_names(self.__class__)

    def clean(self):
        super().clean()
        self._validate_versioned_model()

    @hook(BEFORE_SAVE, when='current_version')
    def _validate_versioned_model(self):
        if self.current_version:
            if len([s for s in self.current_version.split(VERSION_DELIMITER) if s]) < 3:
                # это паттерн
                if not VERSION_PATTERN_REGEX.match(self.current_version):
                    raise ValidationError(ERR_WRONG_VERSION_PATTERN_FORMAT)
            else:
                # это строка с версией
                if not RE_VERSION.match(self.current_version):
                    raise ValidationError(ERR_VERSION_FORMAT.format(self.current_version))

            # валидация существования версии
            self.get_version_by_pattern(self.current_version)

    @property
    def versions_set(self):
        """ Возвращает set связанной модели с версиями по related_name """
        return getattr(self, 'versions')

    def get_version_by_pattern(self, version_pattern_attr: Union[int, str, VersionModel] = None) -> VersionModel:
        """ Возвращает инстанс версии модели по шаблону """
        if not version_pattern_attr:
            if self.current_version:
                version_pattern_attr = self.current_version
            else:
                return self.last_version

        if isinstance(version_pattern_attr, VersionModel):
            return version_pattern_attr

        if isinstance(version_pattern_attr, int):
            return self.versions_set.get(pk=version_pattern_attr)

        if len([s for s in version_pattern_attr.split(VERSION_DELIMITER) if s]) < 3:
            # это паттерн
            version_instance = self.versions_set.annotate(
                exact_version=Func(F('version_arr'), Value(VERSION_DELIMITER), function='array_to_string')
            ).filter(
                exact_version__regex=version_regex(version_pattern_attr)
            ).order_by('-version_arr').first()
            if not version_instance:
                raise ValidationError(f'Версия {version_pattern_attr} для {str(self)} id={self.pk} не существует')
        else:
            # это строка
            try:
                version_instance = self.versions_set.get(version_arr=str_to_int_arr(version_pattern_attr))
            except self.versions_set.model.DoesNotExist:
                raise ValidationError(f'Версия {version_pattern_attr} для {str(self)} id={self.pk} не существует')

        return version_instance

    @property
    def version_list(self) -> List[str]:
        """ Возвращает список версий в виде строк """
        return self.versions_set.annotate(
            exact_version=Func(F('version_arr'), Value(VERSION_DELIMITER), function='array_to_string')
        ).values_list('exact_version', flat=True)

    @property
    def last_version(self) -> Optional[VersionModel]:
        """ Возвращает инстанс последней версии """
        return self.versions_set.order_by('-version_arr').first()

    def is_version_json_changed(self, json_data: dict) -> bool:
        """ Возвращает признак изменения json модели по сравнению с последней сохраненной версией """
        if (last_version := self.last_version) and last_version.hash == get_json_hash(json_data):
            return False
        return True

    @property
    def next_version_str(self) -> str:
        """ Возвращает строку со следующей версией, инкрементированной по минору """
        return next_version_str(self.last_version)

    @transaction.atomic
    def create_or_update_version(self, json_data: dict, version_str: str = None) -> Tuple[bool, VersionModel]:
        """ Создает или обновляет версию """

        # если версия не задана, то создаем следующую только если json изменился
        if not version_str and not self.is_version_json_changed(json_data):
            return False, self.last_version

        version = version_str or self.next_version_str
        if not RE_VERSION.match(version):
            raise ValidationError(ERR_VERSION_FORMAT.format(version))

        model_version, is_created = self.versions_set.get_or_create(
            version_arr=str_to_int_arr(version),
        )
        if not is_created:
            raise ValidationError(f'Версия {version} для {str(self)} уже существует')

        model_version.json = json.loads(json.dumps(json_data, cls=JSONEncoder))
        model_version.save()

        return is_created, model_version


def create_version_model_class(
        module_name: str, model_name: str, version_parent_model: Type[VersionModel],
        model_mixins: Tuple[Type[models.Model]] = None) -> VersionModel:
    """ Фабрика создании модели с версиями """
    lower_name = model_name.lower()
    capitalize_name = model_name.capitalize()
    meta_fields = dict(
        verbose_name=f'{lower_name} version',
        verbose_name_plural=f'{lower_name} versions',
        unique_together=(f'{lower_name}_id', 'version_arr'),
        ordering=(f'{lower_name}_id', 'version_arr'),
    )

    # create class Meta
    class_meta = class_factory(module_name, 'Meta', (version_parent_model.Meta,), {})
    for k, v in meta_fields.items():
        setattr(class_meta, k, v)

    # create class VersionModel
    parents = (*(model_mixins or []), LifecycleModelMixin, version_parent_model)
    version_class = class_factory(module_name, f'{capitalize_name}{VERSION_MODEL_SUFFIX}', parents, {
        lower_name: models.ForeignKey(capitalize_name, related_name='versions', on_delete=models.CASCADE),
        'Meta': class_meta,
    })
    version_class.__str__ = lambda self: f'{getattr(self, lower_name)}:{self.version}'
    version_class._main_model_name = model_name

    return version_class


def is_instance_versioned(instance):
    return isinstance(instance, VersionedModelMixin)
