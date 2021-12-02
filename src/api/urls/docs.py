from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.yasg.generators import LASOpenAPISchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="",
        default_version='v1',
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf='api.urls._documented_api',
    generator_class=LASOpenAPISchemaGenerator,
)

urlpatterns = [
    url(r'^docs/$', schema_view.with_ui('redoc'), name='las_api_docs'),
]
