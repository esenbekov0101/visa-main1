import jwt
from rest_framework.permissions import BasePermission

from main.models import (
    Terminal,
)
from .exceptions import (
    BranchNotFound,
    InvalidTokenFormat,
    InvalidTokenProvided,
    TokenNotProvided,
)
from ..choices import Role


class HasBranch(BasePermission):
    def has_permission(self, request, view):
        if request.user.branch:
            return True
        raise BranchNotFound


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == Role.MANAGER


class IsTerminalAuthenticated(BasePermission):

    def has_permission(self, request, view):
        if token := request.headers.get('Terminal-Authorization'):
            try:
                unverified_payload = jwt.decode(token, options={'verify_signature': False})
                if 'id' in unverified_payload:
                    try:
                        terminal = Terminal.objects.get(id=unverified_payload['id'])
                        try:
                            jwt.decode(token, str(terminal.access_token), 'HS256')
                            setattr(request, 'terminal', terminal)
                            return True
                        except jwt.exceptions.InvalidSignatureError:
                            raise InvalidTokenProvided
                        except jwt.exceptions.PyJWTError:
                            raise InvalidTokenProvided
                        except jwt.exceptions.DecodeError:
                            raise InvalidTokenFormat
                    except Terminal.DoesNotExist:
                        raise InvalidTokenProvided
                raise InvalidTokenProvided
            except jwt.exceptions.DecodeError:
                raise InvalidTokenFormat
        raise TokenNotProvided
