from rest_framework import serializers


class TokenObtainResponseSerializer(serializers.Serializer):
    access = serializers.CharField(label='Access токен')
    refresh = serializers.CharField(label='Refresh токен')


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField(label='Access токен')
