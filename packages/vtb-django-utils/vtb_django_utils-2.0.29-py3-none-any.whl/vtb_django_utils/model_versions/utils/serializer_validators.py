from abc import ABCMeta

from rest_framework import serializers

from .consts import SERIALIZER_VALIDATOR_END_NAME
from .serializers import clean_json_version


# noinspection PyAbstractClass
class VersionedSerializerValidation(serializers.Serializer):
    """ Базовый класс для валидации версионированных сериализаторов """
    __metaclass__ = ABCMeta
    version_field_names = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator_names = self._get_validator_names()
        self.validated_field_names = clean_json_version(self.fields).keys()
        self._serializer_data = None

    def _get_validator_names(self):
        return [func for func in dir(self.__class__)
                if callable(getattr(self.__class__, func)) and func.endswith(SERIALIZER_VALIDATOR_END_NAME)]

    def get_val(self, name_field: str):
        """ Возвращает значение поля с учетом partial_update (если поле не изменяется, то его нет в словаре) """
        if name_field in self._serializer_data:
            return self._serializer_data[name_field]

        elif self.context and self.context['view'].action == 'partial_update':
            if hasattr(self.instance, name_field):
                return getattr(self.instance, name_field)
            elif hasattr(self, 'version_field_names') and name_field in self.version_field_names:
                # TODO нужно сделать тест (что значение берется из версии)
                request = self.context.get('request')
                version_pattern_attr = request.query_params.get('version', '') if request else ''
                return self.instance.get_version_by_pattern(version_pattern_attr).json[name_field]

        raise Exception(f'Field {name_field} not found')

    def validate(self, data: dict) -> dict:
        self._serializer_data = super().validate(data)

        for validator_name in self.validator_names:
            validator_part_name = validator_name.replace(SERIALIZER_VALIDATOR_END_NAME, '')

            # если это валидатор по полю
            if validator_part_name in self.validated_field_names:

                if validator_part_name not in self._serializer_data and self.context['view'].action == 'partial_update':
                    # если значение поля не меняется (при частичном апдейте), пропускаем проверку
                    continue
                self._serializer_data[validator_part_name] = getattr(self.__class__, validator_name)(
                    self, self._serializer_data[validator_part_name])

            else:
                self._serializer_data = getattr(self.__class__, validator_name)(self, self._serializer_data)

        return self._serializer_data
