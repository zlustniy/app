from django.urls import path
from ..views import (
    JWTTokenObtainPairView,
    JWTTokenRefreshView,
)

urlpatterns = [
    path('token/', JWTTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', JWTTokenRefreshView.as_view(), name='token_refresh'),
]
