import inspect
from abc import ABCMeta
from collections import OrderedDict
from functools import wraps
from typing import List

from ..utils.jsondiff import diff
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from .utils.consts import (
    MAIN_SERIALIZER_SUFFIX, SERIALIZER_VERSION_INFO_FIELDS, START_VERSION, REL_VERSION_FIELD_END,
    REL_VERSION_PATTERN_FIELD_END, ERR_VERSIONED_OBJ_NOT_SELECTED, VERSION_PATTERN_REGEX,
    ERR_WRONG_VERSION_PATTERN_FORMAT, VERSION_MODEL_SUFFIX, ERR_SELECTED_VERSION_AND_PATTERN,
    REL_VERSION_CALCULATED_FIELD_END, DOES_NOT_EXIST_VERSION)
from .utils.enums import SerializerType
from .utils.models import get_rel_versioned_field_names_fom_list
from .utils.serializer_validators import VersionedSerializerValidation
from ..utils.inspect import get_module_classes_inheritor, get_class_by_name

model_serializers_map = {}
model_serializers_map_by_name = {}


def register_serializers(module_name: str):
    """ регистрация сериализаторов для моделей """
    global model_serializers_map
    global model_serializers_map_by_name

    # Сериализаторы с версиями
    versioned_serializers = get_module_classes_inheritor(module_name, VersionedModelSerializer)

    # Сериализаторы у которых есть версии (сериализаторы основных моделей и их версий)
    for ver_ser_class in versioned_serializers:
        if not hasattr(ver_ser_class, 'Meta'):
            continue
        main_ser_class = [x for x in inspect.getmro(ver_ser_class) if x.__name__.endswith('MainSerializer')][0]
        model_serializers_map[ver_ser_class.Meta.model] = {
            SerializerType.MAIN: main_ser_class,
            SerializerType.VERSION: ver_ser_class,
        }

    # остальные (неверсионные) сериализаторы моделей (ModelSerializer)
    model_serializers = get_module_classes_inheritor(module_name, serializers.ModelSerializer)
    for model_ser_class in model_serializers:
        if not hasattr(model_ser_class, 'Meta'):
            continue
        if (model_ := model_ser_class.Meta.model) not in model_serializers_map:
            model_serializers_map[model_] = {SerializerType.UNVERSIONED: model_ser_class}

    model_serializers_map_by_name.update({m.__name__: s for m, s in model_serializers_map.items()})


def create_version_decorator(func):
    @wraps(func)
    def __wrap(self, *args, **kwargs):
        validated_data = kwargs.get('validated_data', None) or args[-1]
        version = validated_data.pop('version', None)
        instance = func(self, *args, **kwargs)
        # Апдейтим версию version или создаем новую, если ее нет. Если version не указана, то создаем следующую
        json_data = instance.last_version.json if instance.versions_set.exists() else {}
        json_data.update(self._version_model_json)
        _, self.model_version = instance.create_or_update_version(json_data=json_data, version_str=version)

        return instance

    return __wrap


class VersionedModelSerializer(serializers.ModelSerializer):
    __metaclass__ = ABCMeta
    version = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    last_version = serializers.SerializerMethodField()
    version_list = serializers.SerializerMethodField()
    version_create_dt = serializers.SerializerMethodField()
    version_changed_by_user = serializers.SerializerMethodField()

    # поля которые нужно исключить из json версии (они для запросов по REST)
    exclude_version_json_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_field_names = self._get_main_field_names()
        exclude_fields = (*SERIALIZER_VERSION_INFO_FIELDS, *self.exclude_version_json_fields)
        self.version_field_names = list(filter(
            lambda x: x not in self.main_field_names and x not in exclude_fields,
            self.fields))
        self.model_version = None

    def _get_main_field_names(self) -> list:
        main_serializer_class = [x for x in inspect.getmro(self.__class__)
                                 if x.__name__.endswith(MAIN_SERIALIZER_SUFFIX)]
        return list(main_serializer_class[0]().fields) if main_serializer_class else []

    @staticmethod
    def get_last_version(obj) -> str:
        return obj.last_version.version if obj.last_version else ''

    @staticmethod
    def get_version_list(obj) -> List[str]:
        return obj.version_list

    # noinspection PyUnusedLocal
    def get_version_create_dt(self, obj):
        return self.model_version.create_dt.astimezone().isoformat() if self.model_version else ''

    # noinspection PyUnusedLocal
    def get_version_changed_by_user(self, obj):
        return self.model_version.user.get('username', '') if self.model_version else ''

    @property
    def _main_model_data(self) -> OrderedDict:
        """ возвращает изменяемые поля для основной модели """
        return OrderedDict([(k, v) for k, v in self.validated_data.items() if k in self.main_field_names])

    @property
    def _version_model_json(self) -> dict:
        """ возвращает поля json версии, которые изменяются """
        version_json = {k: v for k, v in self.validated_data.items() if k in self.version_field_names}
        self._update_version_data(version_json)

        return version_json

    # noinspection PyMethodMayBeStatic
    def _update_version_data(self, version_data: dict) -> dict:
        return version_data

    # noinspection PyUnusedLocal
    @transaction.atomic()
    @create_version_decorator
    def create(self, validated_data):
        instance = super().create(self._main_model_data)
        return instance

    # noinspection PyUnusedLocal
    @transaction.atomic()
    @create_version_decorator
    def update(self, instance, validated_data):
        if main_model_data := self._main_model_data:
            instance = super().update(instance, main_model_data)
        return instance

    def to_representation(self, instance):
        # дополняем инстанс модели полями из json версии
        request = self.context.get('request')
        version_pattern_attr = request.query_params.get('version', '') if request else ''
        if self.context and self.context['view'].action == 'partial_update':
            version_instance = instance.last_version
        else:
            version_instance = instance.get_version_by_pattern(version_pattern_attr)
        self.model_version = version_instance

        if self.context and self.context['view'].action == 'create':
            version_data = {k: v for k, v in self.initial_data.items() if k in self.version_field_names}
            # версия не указана - будет создана первая
            version = self.initial_data.get('version', None) or START_VERSION
        else:
            if version_instance:
                version_data = version_instance.json
                version = version_instance.version
            else:
                # метод создания объекта, но не create (например импорт)
                version_data = {}
                version = START_VERSION

            if not (self.context and self.context['view'].action == 'partial_update'):
                try:
                    validated_data = self.validated_data
                except AssertionError:
                    # если validated_data не доступен, то скорее это метод на получение объекта, а не изменение
                    pass
                else:
                    version_data.update({k: v for k, v in validated_data.items() if k in self.version_field_names})
                    if version_str := validated_data.get('version'):
                        version = version_str
                    elif instance.is_version_json_changed(version_data):
                        # если версия не задана, то создаем следующую только если json изменился
                        version = instance.next_version_str

        # дополняем инстанс полями из json версии (чтобы сериализатор не ругался)
        for field_name in self.version_field_names:
            if field_name in version_data:
                setattr(instance, field_name, version_data[field_name])

        representation = super().to_representation(instance)
        representation['version'] = version

        compare_with_version = request.query_params.get('compare_with_version') if request else False
        if version_instance and compare_with_version:
            json_diff = {'compare_with_version': compare_with_version}
            try:
                compare_version_instance = instance.get_version_by_pattern(compare_with_version)
            except version_instance.__class__.model.DoesNotExist:
                json_diff['err'] = DOES_NOT_EXIST_VERSION.format(compare_with_version)
            else:
                origin_version_json = version_instance.json
                compare_version_json = compare_version_instance.json
                json_diff['diff'] = diff(compare_version_json or type(compare_version_json)(), origin_version_json)
                json_diff['changed_by_user'] = compare_version_instance.changed_by_user
            representation['version_diff'] = json_diff

        return representation


# noinspection PyAbstractClass
class WithVersionedRelationsSerializer(VersionedSerializerValidation):
    """ Сериализатор использующий связанные версионные сущности (например граф в экшене) """
    __metaclass__ = ABCMeta
    models_module_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rel_versioned_fields = get_rel_versioned_field_names_fom_list(self.fields.keys())

    @staticmethod
    def _get_rel_class_name(rel_field_name: str) -> str:
        """ Возвращает имя поля по имени реляции """
        return rel_field_name.capitalize()

    def _get_rel_model_version(self, instance_dict: dict, rel_field_name: str) -> str:
        """ Возвращает строку версии с учетом выбранной версии и шаблона """
        if rel_version_model_id := instance_dict.get(f'{rel_field_name}_id', instance_dict.get(rel_field_name)):
            rel_class_name = self._get_rel_class_name(rel_field_name)
            rel_model_class = get_class_by_name(self.models_module_name, rel_class_name)
            rel_instance = rel_model_class.objects.get(pk=rel_version_model_id)
            rel_version = instance_dict.get(f'{rel_field_name}{REL_VERSION_FIELD_END}')
            rel_version_pattern = instance_dict.get(f'{rel_field_name}{REL_VERSION_PATTERN_FIELD_END}')
            rel_version_model = rel_instance.get_version_by_pattern(rel_version or rel_version_pattern)
            if rel_version_model:
                return rel_version_model.version
        return ''

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for rel_field in self.rel_versioned_fields:
            # calculated версия для связанной сущности
            calc_field_name = f'{rel_field}{REL_VERSION_CALCULATED_FIELD_END}'
            representation[calc_field_name] = self._get_rel_model_version(representation, rel_field)
        return representation

    def versioned_instance_not_selected_validator(self, data: dict) -> dict:
        """ Проверка что если задана ее версия или шаблон, то модель с версией тоже выбрана """
        for rel_field in self.rel_versioned_fields:
            rel_instance_id = self.get_val(f'{rel_field}_id')
            version = self.get_val(f'{rel_field}{REL_VERSION_FIELD_END}')
            version_pattern = self.get_val(f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')
            if (version or version_pattern) and not rel_instance_id:
                raise ValidationError(ERR_VERSIONED_OBJ_NOT_SELECTED.format(rel_field.capitalize()))

        return data

    def version_pattern_format_validator(self, data: dict) -> dict:
        """ Проверяет формат паттерна версии """
        for rel_field in self.rel_versioned_fields:
            version_pattern = self.get_val(f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')
            if version_pattern and not VERSION_PATTERN_REGEX.match(version_pattern):
                raise ValidationError(ERR_WRONG_VERSION_PATTERN_FORMAT)

        return data

    def versioned_instance_not_match_version_validator(self, data: dict) -> dict:
        """ Проверка что выбраная модель с версией и выбранная версия соответствуют """
        for rel_field in self.rel_versioned_fields:
            if not (rel_instance_id := self.get_val(f'{rel_field}_id')):
                continue

            version = self.get_val(f'{rel_field}{REL_VERSION_FIELD_END}')
            version_pattern = self.get_val(f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')

            rel_class_name = self._get_rel_class_name(rel_field)
            version_model_class_name = f'{rel_class_name}{VERSION_MODEL_SUFFIX}'
            version_model_class = get_class_by_name(self.models_module_name, version_model_class_name)
            rel_instance_id_name = f'{rel_class_name.lower()}_id'

            # проверяем что такая версия существует
            version_model_class.get_instance_by_pattern(
                rel_instance_id_name, rel_instance_id, version or version_pattern)

        return data

    def select_version_and_pattern_validator(self, data: dict) -> dict:
        """ Нельзя выбрать версию и шаблон версии одновременно """
        for rel_field in self.rel_versioned_fields:
            version = self.get_val(f'{rel_field}{REL_VERSION_FIELD_END}')
            version_pattern = self.get_val(f'{rel_field}{REL_VERSION_PATTERN_FIELD_END}')
            if version and version_pattern:
                raise ValidationError(ERR_SELECTED_VERSION_AND_PATTERN.format(self.__class__.__name__))

        return data
