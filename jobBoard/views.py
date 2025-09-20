from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User
from .serializers import UserSerializer, EmailAuthTokenSerializer

class SignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        name = data.get("name", "")
        first_name = ""
        last_name = ""

        if name:
            name_parts = name.strip().split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        data["first_name"] = first_name
        data["last_name"] = last_name
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

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
            "user_id": user.id,
            "email": user.email
        }, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "token": token.key,
            "user_id": user.id,
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


class HelloView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "user_id": user.id,
            "email": user.email,
            "message": "Hello, authenticated user!"
        }, status=status.HTTP_200_OK)