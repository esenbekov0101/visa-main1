import jwt
from django.db.transaction import atomic
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import ViewSetMixin

from .. import permissions as perm
from .. import serializers as srz


class TerminalViewSet(ViewSetMixin,
                      GenericAPIView):

    def get_serializer_class(self):
        if self.action == 'get_token':
            return srz.TerminalLoginObtainPair
        if self.action == 'student_check':
            return srz.TerminalStudentCheckSerializer
        if self.action == 'payment_create':
            return srz.TerminalStudentPaySerializer

    def get_permissions(self):
        if self.action == 'get_token':
            return AllowAny(),
        return perm.IsTerminalAuthenticated(),

    # noinspection PyTypeChecker
    @action(['post'], False, 'get-token')
    @swagger_auto_schema(responses={status.HTTP_201_CREATED: srz.TerminalLoginResponseSerializer})
    def get_token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = {'id': serializer.validated_data['id']}
        data = {'token': jwt.encode(payload, str(serializer.validated_data['access_token']))}
        return Response(data, status.HTTP_201_CREATED)

    # noinspection PyTypeChecker
    @action(['get'], False, 'student-check')
    @swagger_auto_schema(query_serializer=srz.TerminalStudentCheckSerializer)
    def student_check(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status.HTTP_200_OK)

    # noinspection PyTypeChecker
    @action(['post'], False, 'payment-create')
    @swagger_auto_schema(responses={status.HTTP_201_CREATED: srz.TerminalStudentPayResponseSerializer})
    @atomic
    def payment_create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status.HTTP_201_CREATED)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}