from enum import Enum


class SerializerType(Enum):
    MAIN = 'main'
    VERSION = 'version'
    UNVERSIONED = 'unversioned'
    NON_MODEL = 'non_model'
