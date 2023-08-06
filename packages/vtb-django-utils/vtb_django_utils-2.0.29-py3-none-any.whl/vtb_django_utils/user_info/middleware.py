from datetime import datetime

from vtb_django_utils.utils.consts import DATETIME_SHORT_FORMAT
from .info import set_user_info


class UserInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_user_info(request)
        response = self.get_response(request)
        return response

    @staticmethod
    def _format_value(value):
        if isinstance(value, datetime):
            return value.strftime(DATETIME_SHORT_FORMAT)
        return value
