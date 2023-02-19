from django.contrib.auth import get_user
from django.utils.functional import SimpleLazyObject
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from .. import serializers as srz


class TokenViewSet(ViewSetMixin,
                   GenericAPIView):
    def get_serializer_class(self):
        if self.action == 'create':
            return TokenObtainPairSerializer
        if self.action == 'refresh':
            return TokenRefreshSerializer
        return TokenObtainPairSerializer

    # noinspection PyTypeChecker
    @swagger_auto_schema(responses={status.HTTP_201_CREATED: srz.TokenObtainPairResponseSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response({
                **serializer.validated_data,
                'role': serializer.user.role,
                'branch': serializer.user.branch.name,
                'fullname': serializer.user.fullname,
                'inn': serializer.user.inn,
        }, status=status.HTTP_200_OK)

    #noinspection PyTypeChecker
    @action(['post'], False, 'refresh')
    @swagger_auto_schema(responses={status.HTTP_200_OK: srz.TokenRefreshResponseSerializer})
    def refresh(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)


        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response({
            **serializer.validated_data,
            'role': serializer.user.role,
            'branch': serializer.user.branch.name,
            'fullname': serializer.user.fullname,
        }, status=status.HTTP_200_OK)

