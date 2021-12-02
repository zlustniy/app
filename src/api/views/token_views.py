from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .token_serializers import (
    TokenObtainResponseSerializer,
    TokenRefreshResponseSerializer,
)


@method_decorator(name='post', decorator=swagger_auto_schema(
    security=[],
    operation_description=(
            'Метод предназначен для получения JWT access и refresh токенов с помощью логина и пароля.<br>'
            'Срок жизни access токена - 15 минут<br>'
            'Срок жизни refresh токена - 1 день. С помощью refresh токена и метода [token_refresh](#operation/token_refresh) '
            'можно получать новый access токен без необходимости передавать логин и пароль.<br>'
            'Полученный access токен необходимо подставить в заголовок `Authorization` при работе с методами api.'
    ),
    request_body=TokenObtainSerializer,
    responses={
        200: TokenObtainResponseSerializer(),
    },
    operation_id='token_obtain_pair'
))
class JWTTokenObtainPairView(TokenObtainPairView):
    pass


@method_decorator(name='post', decorator=swagger_auto_schema(
    security=[],
    operation_description=(
            'Метод предназначен для получения JWT access токена с помощью refresh токена.<br>'
            'Срок жизни access токена - 15 минут<br>'
            'Полученный access токен необходимо подставить в заголовок `Authorization` при работе с методами api.'
    ),
    request_body=TokenRefreshSerializer,
    responses={
        200: TokenRefreshResponseSerializer(),
    },
    operation_id='token_refresh'
))
class JWTTokenRefreshView(TokenRefreshView):
    pass
