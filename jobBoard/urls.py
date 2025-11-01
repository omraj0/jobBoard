from django.urls import path
from .views import SignupView, LoginView, LogOutView, ForgotPasswordView, ResetPasswordView, HelloView

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogOutView.as_view(), name='logout'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('hello/', HelloView.as_view(), name='hello'),
]