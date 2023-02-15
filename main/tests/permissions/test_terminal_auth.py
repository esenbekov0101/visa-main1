import jwt
from django.http import HttpRequest
from django.test import TestCase

from main.models import (
    Terminal, )
from ...permissions.exceptions import (
    InvalidTokenFormat,
    InvalidTokenProvided,
    TokenNotProvided,
)
from ...permissions import (
    IsTerminalAuthenticated,
)


class TerminalAuthTest(TestCase):

    def setUp(self):
        self.terminal = Terminal.objects.create(name='terminal 1', access_token=1324500091)
        self.request = HttpRequest()
        self.authenticator = IsTerminalAuthenticated()

    def test_auth_token(self):
        self.request.META['HTTP_TERMINAL_AUTHORIZATION'] = jwt.encode({'id': self.terminal.id},
                                                                      str(self.terminal.access_token))
        self.assertTrue(self.authenticator.has_permission(self.request, None))

    def test_token_not_provided_negative(self):
        self.assertRaises(TokenNotProvided, self.authenticator.has_permission, self.request, None)

    def test_invalid_token_format_negative(self):
        self.request.META['HTTP_TERMINAL_AUTHORIZATION'] = 'Bearer ' + jwt.encode({'id': self.terminal.id},
                                                                                  str(self.terminal.access_token))
        self.assertRaises(InvalidTokenFormat, self.authenticator.has_permission, self.request, None)

    def test_invalid_token_negative(self):
        self.request.META['HTTP_TERMINAL_AUTHORIZATION'] = jwt.encode({'id': self.terminal.id},
                                                                      str(self.terminal.access_token) + '2')
        self.assertRaises(InvalidTokenProvided, self.authenticator.has_permission, self.request, None)
