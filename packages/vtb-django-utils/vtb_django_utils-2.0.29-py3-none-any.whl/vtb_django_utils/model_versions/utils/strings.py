from typing import Union

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError

from .consts import VERSION_DELIMITER, VERSION_PART_LEN, VERSION_PART_COUNT, ERR_VERSION_COUNTER_FULL, START_VERSION


def str_to_int_arr(version: str):
    return list(map(int, version.split(VERSION_DELIMITER)))


def int_arr_to_str(version_arr: Union[list, tuple, ArrayField]):
    return VERSION_DELIMITER.join(map(str, version_arr))


def is_last_version_less(last_version: str, new_version: str) -> bool:
    """ Сравнивает две версии в виде строк по значению """
    if last_version:
        last_version_parts = str_to_int_arr(last_version)
        new_version_parts = str_to_int_arr(new_version)
        for last, new in zip(last_version_parts, new_version_parts):
            if int(last) < int(new):
                return True
    return False


def next_version_str(last_version) -> str:
    """ Возвращает строку со следующей версией, инкрементированной по минору """
    if last_version and last_version.version_arr:
        # noinspection PyTypeChecker
        number_as_str = ''.join([f'{x:03}' for x in list(last_version.version_arr)])
        next_number = int(number_as_str) + 1
        max_number = int(VERSION_PART_LEN * '9' * VERSION_PART_COUNT)
        if next_number > max_number:
            raise ValidationError(ERR_VERSION_COUNTER_FULL.format(last_version.version_arr))

        next_number_as_str = f'{next_number:0{VERSION_PART_LEN * VERSION_PART_COUNT}}'
        return VERSION_DELIMITER.join([
            str(int(next_number_as_str[i * VERSION_PART_LEN: i * VERSION_PART_LEN + VERSION_PART_LEN]))
            for i in range(VERSION_PART_COUNT)])
    else:
        return START_VERSION
