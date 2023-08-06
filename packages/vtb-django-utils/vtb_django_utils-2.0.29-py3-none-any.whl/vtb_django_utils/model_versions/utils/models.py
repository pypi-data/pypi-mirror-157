import operator
from typing import Tuple, Iterable, List, Set, Type

from django.db import models

from vtb_django_utils.model_versions.utils.consts import REL_VERSION_FIELD_END, REL_VERSION_PATTERN_FIELD_END
from vtb_django_utils.utils.db import get_model_field_names


def get_all_available_major_version(versions: Iterable[List[int]]) -> List[Tuple[str, str]]:
    all_version: Set[tuple] = set()
    for version in versions:
        all_version.add((f'{version[0]}.', f'{version[0]}.x.x'))
        all_version.add((f'{version[0]}.{version[1]}.', f'{version[0]}.{version[1]}.x'))
    return sorted((version for version in all_version), key=operator.itemgetter(1))


def get_rel_versioned_field_names(model_class: Type[models.Model]) -> set:
    """ Возвращает имена полей связанной версионной модели """
    def _get_fields(pattern):
        return set([f.replace(pattern, '') for f in field_names if f.endswith(pattern)])

    field_names = get_model_field_names(model_class)
    rel_fields = set(_get_fields(REL_VERSION_FIELD_END)) & set(_get_fields(REL_VERSION_PATTERN_FIELD_END))
    return rel_fields


def get_rel_versioned_field_names_fom_list(field_names: Iterable[str]) -> set:
    """ Возвращает имена полей связанной версионной модели из списка имен полей """
    def _get_fields(pattern):
        return set([f.replace(pattern, '') for f in field_names_set if f.endswith(pattern)])

    field_names_set = set(field_names)
    rel_fields = set(_get_fields(f'{REL_VERSION_FIELD_END}')) & set(_get_fields(REL_VERSION_PATTERN_FIELD_END))
    return rel_fields
