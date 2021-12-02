from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors.view import SwaggerAutoSchema
from drf_yasg.utils import is_list_view
from rest_framework import exceptions, status
from rest_framework.settings import api_settings


class LASAutoSchema(SwaggerAutoSchema):
    field_inspectors = swagger_settings.DEFAULT_FIELD_INSPECTORS

    @staticmethod
    def get_detail_error():
        return openapi.Schema(type=openapi.TYPE_STRING, description='Детали ошибки')

    def get_generic_error_schema(self):
        return openapi.Schema(
            _('Общая ошибка'),
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': self.get_detail_error()
            },
            required=['detail']
        )

    def get_bad_request_error_schema(self):
        return openapi.Schema(
            _('Ошибка запроса.'),
            type=openapi.TYPE_OBJECT,
            properties={
                api_settings.NON_FIELD_ERRORS_KEY: openapi.Schema(
                    description=_('Список ошибок валидации, не связанных с конкретным параметром'),
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)
                ),
                'detail': self.get_detail_error(),
            },
            additional_properties=openapi.Schema(
                description=_('Список ошибок валидации конкретного параметра'),
                type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)
            ),
        )

    def get_response_serializers(self):
        responses = super().get_response_serializers()
        definitions = self.components.with_scope(
            openapi.SCHEMA_DEFINITIONS)  # type: openapi.ReferenceResolver

        definitions.setdefault('GenericError', self.get_generic_error_schema)
        definitions.setdefault('BadRequestError', self.get_bad_request_error_schema)
        definitions.setdefault('APIException', self.get_generic_error_schema)

        if self.get_request_serializer() or self.get_query_serializer():
            responses.setdefault(400, openapi.Response(
                description=_('Ошибка запроса.'),
                schema=openapi.SchemaRef(definitions, 'BadRequestError')
            ))

        security = self.get_security()
        if security is None or len(security) > 0:
            responses.setdefault(status.HTTP_401_UNAUTHORIZED, openapi.Response(
                description=_('Ошибка авторизации.'),
                schema=openapi.SchemaRef(definitions, 'GenericError')
            ))
            responses.setdefault(status.HTTP_403_FORBIDDEN, openapi.Response(
                description=_("Доступ запрещен."),
                schema=openapi.SchemaRef(definitions, 'GenericError')
            ))
        if not is_list_view(self.path, self.method, self.view):
            responses.setdefault(exceptions.PermissionDenied.status_code, openapi.Response(
                description=_("Доступ запрещен."),
                schema=openapi.SchemaRef(definitions, 'APIException')
            ))
            responses.setdefault(exceptions.NotFound.status_code, openapi.Response(
                description=_('Объект не найден или недостаточно прав для доступа'),
                schema=openapi.SchemaRef(definitions, 'APIException')
            ))

        if self.view.throttle_classes:
            responses.setdefault(exceptions.Throttled.status_code, openapi.Response(
                description=_('Слишком много запросов'),
                schema=openapi.SchemaRef(definitions, 'GenericError')
            ))

        responses.setdefault(exceptions.APIException.status_code, openapi.Response(
            description=_('Серверная ошибка.'),
            schema=openapi.SchemaRef(definitions, 'APIException')
        ))

        return responses
