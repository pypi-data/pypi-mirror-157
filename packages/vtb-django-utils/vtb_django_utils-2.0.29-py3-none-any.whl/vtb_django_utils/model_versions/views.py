from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from vtb_django_utils.model_versions.serializers import model_serializers_map
from vtb_django_utils.model_versions.utils.enums import SerializerType
from vtb_django_utils.user_info.views import SetUserInfoMixin


class VersionMixin(SetUserInfoMixin, UpdateModelMixin, GenericViewSet):

    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        instance = self.get_object()
        data = dict(result.data)
        version_instance = instance.get_version_by_pattern(data['version'])
        data.update({
            'last_version': instance.last_version.version if instance.last_version else '',
            'version_create_dt': version_instance.create_dt.astimezone().isoformat(),
            'version_changed_by_user': version_instance.user.get('username'),
        })
        return Response(data)

    def get_serializer_class(self):
        if self.action == 'list':
            return model_serializers_map[self.queryset.model][SerializerType.MAIN]

        if self.detail and self.get_object().versions_set.count() == 0:
            # для одиночных запросов, если нет версии у объекта - отдаем сериализатор для модели
            return model_serializers_map[self.queryset.model][SerializerType.MAIN]

        return model_serializers_map[self.queryset.model][SerializerType.VERSION]

    # noinspection PyUnusedLocal
    @action(methods=["GET"], detail=True, url_name='version_list')
    def version_list(self, request, pk: int, *args, **kwargs):
        obj = self.get_object()
        return Response(obj.version_list)

    def get_queryset(self):
        queryset = super(VersionMixin, self).get_queryset()
        if not self.detail:
            # для списков отдаем только объекты с версиями
            queryset = queryset.exclude(versions__isnull=True)
        return queryset
