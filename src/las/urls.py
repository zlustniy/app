from appversion.views import VersionAPIView
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/version/', VersionAPIView.as_view()),

    path('api/', include('api.urls')),
]
