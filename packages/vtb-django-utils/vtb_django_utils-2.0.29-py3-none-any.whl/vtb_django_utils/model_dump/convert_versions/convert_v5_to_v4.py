from copy import deepcopy

from vtb_django_utils.model_dump.consts import REL_MODELS_FOREIGN_KEY, REL_MODELS_REVERS_KEY


def convert_v5_to_v4(object_dump: dict):
    """ Преобразует данные дампа из версии 5.0 в версию 4.0 """
    new_dump = deepcopy(object_dump)
    model_name = new_dump['model_name']
    new_dump[model_name]['json'] = new_dump[model_name]
    if 'current_version' in new_dump[model_name] and new_dump[model_name]['current_version'] is None:
        new_dump[model_name]['json']['current_version'] = ''

    for rel_type_key in (REL_MODELS_FOREIGN_KEY, REL_MODELS_REVERS_KEY):
        for rel_key, rel_value in new_dump.get(rel_type_key, {}).items():
            if isinstance(rel_value, list):
                for i, rel_item in enumerate(rel_value):
                    rel_value[i] = convert_v5_to_v4(rel_item)

            elif isinstance(rel_value, dict):
                new_dump[rel_type_key][rel_key] = convert_v5_to_v4(rel_value)

            else:
                raise Exception(
                    f'Ошибка импорта {model_name=} {new_dump[model_name]["id"]} {rel_key} is {type(rel_value)}')

    return new_dump
