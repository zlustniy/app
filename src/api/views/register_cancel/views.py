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
from .serializers import (
    RegisterCancelInputSerializer,
    RegisterCancelResponseSerializer,
)


@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description=_('Метод снятия с учёта заявки.'),
    request_body=RegisterCancelInputSerializer,
    responses={
        200: RegisterCancelResponseSerializer(_('Снято с учета'), many=True),
    },
    operation_id='register_cancel',
))
class RegisterCancelAPIView(APIView):
    http_method_names = ['post']
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, HasInstance,)
    swagger_schema = LASAutoSchema
    request_serializer_class = RegisterCancelInputSerializer
    response_serializer_class = RegisterCancelResponseSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.request_serializer_class(
            data=request.data,
            context={
                'user': request.user,
            }
        )
        serializer.is_valid(raise_exception=True)
        cancel_results = LiabilityAccountingSystem(
            user=request.user,
        ).cancel(
            payload=serializer.validated_data['payload'],
        )
        response_serializer = self.response_serializer_class(data=cancel_results, many=True)
        response_serializer.is_valid(raise_exception=True)

        return Response(
            data=response_serializer.validated_data,
            status=status.HTTP_200_OK,
        )
