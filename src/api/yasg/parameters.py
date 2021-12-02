from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi

token = openapi.Parameter(
    name='Authorization',
    in_=openapi.IN_HEADER,
    description=_('Заголовок авторизации'),
    type=openapi.TYPE_STRING,
    required=True,
)
