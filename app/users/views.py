from rest_framework import viewsets, permissions, status, generics
from app.users.serializers import (
    CompanySerializer,
    CustomerSerializer,
    RegisterSerializer,
    LoginSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    ChangePasswordSerializer,
)
from app.users.models import Company, Customer, User
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import Util
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        return Company.objects.filter(email=user)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Customer.objects.all()
        return Customer.objects.filter(
            Q(company_name=user) | Q(id=self.request.user.id)
        )


class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        email = request.data["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            absurl = "http://" + current_site + relativeLink
            email_body = "Hi, use the link below to reset your password \n" + absurl

            data = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "Reset your password",
            }
            Util.send_email(data)
        return Response(
            {"success": "We have send your a link to reset your password"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Token not valid"}, status=status.HTTP_401_UNAUTHORIZED
                )

            return Response(
                {
                    "success": True,
                    "message": "Credentials Valid",
                    "uidb64": uidb64,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Token not valid"}, status=status.HTTP_401_UNAUTHORIZED
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset success"},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
