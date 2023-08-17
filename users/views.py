from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email, check_email_or_phone
from .serializers import SignUpSerializer, ChangeUserInformationSerializer, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer, LogOutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .models import User, CODE, NEW, VIA_EMAIL, VIA_PHONE


class CreateUserApiView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer


class VerifyApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                'status': True,
                'auth_status': user.auth_status,
                'access': user.token()['access'],
                'refresh': user.token()['refresh_token'],
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.confirmation.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                'message': "Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        verifies.is_confirmed = True
        if user.auth_status == NEW:
            user.auth_status = CODE
            user.save()
        return True


class GetNewVerificationApiVie(APIView):
    def get(self, request, *args, **kwargs):
        print(request.user)
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone, code)

        else:
            data = {
                'status': False,
                'message': "Email yoki telefon raqami noto'g'ri kiritildi",
            }
            raise ValidationError(data)

        return Response({
            'success': True,
            'message': "Tasdiqlash kodingiz qaytadan jo'natildi",
        })

    @staticmethod
    def check_verification(user):
        verifies = user.confirmation.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                'status': False,
                'message': 'Kodingiz hali ishlatish uchun yaroqli, iltimos, biroz kutib turing'
            }
            raise ValidationError(data)


class ChangeUserInformationApiView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUserInformationSerializer
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationApiView, self).update(request, *args, **kwargs)
        data = {
            'status': True,
            'message': "User updated successfully",
            'auth_status': request.user.auth_status
        }
        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationApiView, self).partial_update(request, *args, **kwargs)
        data = {
            'status': True,
            'message': "User updated successfully",
            'auth_status': request.user.auth_status
        }
        return Response(data, status=status.HTTP_200_OK)


class ChangeUserPhotoApiView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {
                    'message': "Rasm muvaffaqiyatli o'zgartirildi"
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class LoginApiView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshApiView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LogOutSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success": True,
                "message": "You are successfully logged out"
            }
            return Response(data, status=205)
        except TokenError:
            return Response(status=400)


class ForgotPasswordApiView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_phone_number = serializer.validated_data.get('email_phone_number')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_phone_number) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone, code)
        elif check_email_or_phone(email_phone_number) == "email":
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)

        return Response({
            "success": True,
            'message': "Tasdiqlash kodi muvaffaqiyatli yuborildi",
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token'],
            "user_auth_status": user.auth_status,
        }, status=200)


class ResetPasswordApiView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordApiView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="User not found")
        return Response({
            'success': True,
            'message': "Parolingiz muvaffaqiyatli o'zgartirildi",
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token']
        })


