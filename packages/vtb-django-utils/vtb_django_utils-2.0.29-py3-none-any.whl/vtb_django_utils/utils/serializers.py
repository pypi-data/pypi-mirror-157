from functools import lru_cache
from typing import Type

from rest_framework import serializers


@lru_cache
def null_allowed_serializer_field_names(serializer_class: Type[serializers.Serializer]) -> list:
    """ Возвращает поля сериализатора с разрешенным нулем (необязательные поля) """
    return [name for name, field in serializer_class().fields.items() if field.allow_null]
