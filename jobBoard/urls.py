from django.urls import path
from .views import SignupView, LoginView, LogOutView, HelloView

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogOutView.as_view(), name='logout'),
    path('hello/', HelloView.as_view(), name='hello'),
]