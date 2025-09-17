from django.urls import path
from .views import CustomAuthToken

urlpatterns = [
    path('auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),
]