from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

import yagmail
from .models import User
from .serializers import UserSerializer, EmailAuthTokenSerializer

from django.conf import settings
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        name = data.get("name", "")
        first_name = ""
        last_name = ""

        if name:
            name_parts = name.strip().split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        data["first_name"] = first_name
        data["last_name"] = last_name
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "Email is already registered. Please login instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Signup successful",
            "token": token.key,
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = EmailAuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "token": token.key,
            "email": user.email
        }, status=status.HTTP_200_OK)


class LogOutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},status=status.HTTP_401_UNAUTHORIZED)
        
        user.auth_token.delete()
        return Response({
            "email": user.email,
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)


class CheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_staff": user.is_staff,
            "message": "User authentication verified successfully."
        }, status=status.HTTP_200_OK)
    

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.RESET_URL}/{uid}/{token}"

        try:
            first_name = user.first_name if user.first_name else "User"
            mail = yagmail.SMTP(user=settings.YAGMAIL_USER, password=settings.YAGMAIL_PASSWORD)
            subject = "Password Reset Request"
            content = f"Hello {first_name},\n\nClick the link below to reset your password:\n\n{reset_link}\n\nIf you didn’t request this, ignore this email."
            mail.send(to=email, subject=subject, contents=content)
        except Exception as e:
            return Response({"message": "If the email is registered, a reset link will be sent."}, status=status.HTTP_200_OK)

        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
    

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)