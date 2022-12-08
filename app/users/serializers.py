from rest_framework import serializers
from app.users.models import Company, Customer, User
from app.users.base64 import Base64ImageField
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = [
            "url",
            "name",
            "address",
            "city",
            "district",
            "email",
            "cnpj",
            "is_active",
            "password",
        ]


class CustomerSerializer(serializers.HyperlinkedModelSerializer):

    documents = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Customer
        fields = [
            "url",
            "name",
            "cpf",
            "email",
            "is_active",
            "password",
            "company_name",
            "documents",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = Company
        fields = ["email", "name", "cnpj", "password"]

    def validade(self, attrs):
        return attrs

    def create(self, validated_data):
        return Company.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=3, write_only=True)
    tokens = serializers.CharField(max_length=68, min_length=3, read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")
        if not user.is_active:
            raise AuthenticationFailed("Account is not active")

        return {"email": user.email, "name": user.name, "tokens": user.tokens()}


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:

            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)

            user.set_password(password)
            user.save()
            return user
        except:
            raise AuthenticationFailed("The reset link is invalid (exception)", 401)


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
