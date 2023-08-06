from vtb_django_utils.model_versions.utils.consts import SERIALIZER_VERSION_INFO_FIELDS


class PassCreateUpdateMixin:
    """ Для имитации реализации абстрактных методов """
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


def clean_json_version(data: dict):
    return {k: v for k, v in data.items() if k not in set(SERIALIZER_VERSION_INFO_FIELDS)}
