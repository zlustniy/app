from django.urls import path, include

from ..views import (
    RegisterAddAPIView,
    RegisterCancelAPIView,
    RegisterEditAPIView,
)

urlpatterns = [
    path('', include('api.urls.auth_urls')),

    path('register/add/', RegisterAddAPIView.as_view(), name='register_add'),
    path('register/cancel/', RegisterCancelAPIView.as_view(), name='register_cancel'),
    path('register/edit/', RegisterEditAPIView.as_view(), name='register_edit'),
]
