from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)


class TokenNotProvided(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = _('Terminal-Authorization Token not provided')


class InvalidTokenFormat(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = _('Terminal-Authorization Token format is invalid')


class InvalidTokenProvided(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = _('Invalid Terminal-Authorization token provided')


class BranchNotFound(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_detail = _('For this action you must to have a branch')
