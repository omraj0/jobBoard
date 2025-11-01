from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    print("Inside UserSerializer")

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        print("Creating user with data:", validated_data)
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        return user

class EmailAuthTokenSerializer(serializers.Serializer):
    print("Inside EmailAuthTokenSerializer")
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        print("Validating with attrs")
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError(_("Unable to log in with provided credentials.") ,code='authorization')
        else:
            raise serializers.ValidationError(_('Must include "email" and "password".'), code='authorization',)

        attrs['user'] = user
        return attrs