from django.urls import path
from .views import SignupView, LoginView, LogOutView, ForgotPasswordView, ResetPasswordView, CheckView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('check/', CheckView.as_view(), name='check'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
]