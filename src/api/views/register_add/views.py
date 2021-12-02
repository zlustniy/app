from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.permissions import HasInstance
from api.yasg.schemas import LASAutoSchema
from las.services.las import LiabilityAccountingSystem
from las.services.tools.subject_accumulation import SubjectAccumulationManager
from .serializers import (
    RegisterAddInputSerializer,
    RegisterAddResponseWrappedSerializer,
)


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description=_('Метод постановки на учёт заявки.'),
    request_body=RegisterAddInputSerializer,
    responses={
        200: RegisterAddResponseWrappedSerializer(_('Поставлено на учет'), many=True),
    },
    operation_id='register_add',
))
class RegisterAddAPIView(APIView):
    http_method_names = ['post']
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, HasInstance,)
    swagger_schema = LASAutoSchema
    request_serializer_class = RegisterAddInputSerializer
    response_serializer_class = RegisterAddResponseWrappedSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.request_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        increment_results = LiabilityAccountingSystem(
            user=request.user,
        ).add(
            subject_accumulation=SubjectAccumulationManager.get_entity(
                external_id=serializer.validated_data['subject_ogrn'],
                external_description=serializer.validated_data.get('subject_name'),
            ),
            payload=serializer.validated_data['payload'],
        )

        response_serializer = self.response_serializer_class(data={
            'request_id': serializer.validated_data.get('request_id'),
            'payload': increment_results,
        })
        response_serializer.is_valid()

        return Response(
            data=response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )
