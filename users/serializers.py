from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from .models import User, UserConfirmation, DONE, CODE, PHOTO, NEW
from shared.utility import check_email_or_phone, send_email, check_user_type


class SignUpSerializer(serializers.ModelSerializer):
    # id = serializers.UUIDField(read_only=True)  # manashu uchun unique bo'lmagan id ni tanlab xatolik kelib chiqqan

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(max_length=221, required=False)

    class Meta:
        model = User
        fields = ['id', 'auth_type', 'auth_status']

        extra_kwargs = {
            'auth_type': {'required': False, 'read_only': True},
            'auth_status': {'required': False, 'read_only': True},
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        print('auth_type_user', user.auth_type)
        if user.auth_type == 'via_phone':
            code = user.create_verify_code('via_phone')
            print('code', code)
            send_email(user.phone, code)
        elif user.auth_type == 'via_email':
            code = user.create_verify_code('via_email')
            print('code', code)
            send_email(user.email, code)
            # send_phone_code(phone, code)
        user.save()
        return user

    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                'status': False,
                'message': 'This email already exist on database',
            }
            raise ValidationError(data)

        elif value and User.objects.filter(phone=value).exists():
            data = {
                'status': False,
                'message': 'This phone already exist on database',
            }
            raise ValidationError(data)
        return value

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(attr):
        data = str(attr.get('email_phone_number')).lower()
        input_data = data
        print(1)
        auth_type = check_email_or_phone(input_data)
        print(2)
        print('auth_type', auth_type)
        print('input_data', input_data)

        if auth_type == 'phone':
            data = {
                'phone': input_data,
                'auth_type': 'via_phone'
            }
        elif auth_type == 'email':
            data = {
                'email': input_data,
                'auth_type': 'via_email'
            }
        elif auth_type == 'error':
            raise ValidationError({
                'status': False,
                'message': "telefon raqami yoki email xato to'ldirildi",
            })
        else:
            raise ValidationError({
                'status': False,
                'message': "you must send phone or email",
            })
        return data

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class ChangeUserInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    'message': "Parolingiz va tasdiqlash parolingiz teng emas !"
                }
            )
        if password and confirm_password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError({
                'message': "Username must be between 5 and 30 characters long"
            })
        if username.isdigit():
            raise ValidationError({
                'message': "This username is entirely numeric"
            })
        return username

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE:
            instance.auth_status = DONE
            instance.save()
        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=('jpg', 'jpeg', 'png', 'heic', 'heif'))])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['user_input'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(read_only=True, required=False)

    def auth_validate(self, data):
        print(data)
        user_input = data.get('user_input')  # email, phone or username
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone=user_input)
            username = user.username

        else:
            data = {
                'success': True,
                'message': "Siz Email, Username yoki Telefon raqamingizni kiritishingiz kerak"
            }
            raise ValidationError(data)

        authentication_kwargs = {
            self.username_field: username,
            'password': data.get('password'),
        }

        current_user = User.objects.filter(username__iexact=username).first()

        if current_user and current_user.auth_status in [NEW, CODE]:
            raise ValidationError({
                'success': False,
                'message': "Siz ro'yxatdan to'liq o'tmagansiz"
            })

        user = authenticate(**authentication_kwargs)
        if user:
            self.user = user
        else:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Kechirasiz login yoki parolingiz xato iltimos qayta urinib ko'ring"
                }
            )

    def validate(self, data):
        print("data", data)
        self.auth_validate(data)
        if self.user.auth_status in [NEW, CODE]:
            raise PermissionDenied(
                "Siz login qila olmaysiz. Ruxsatingiz yo'q"
            )
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        return data

    def get_user(self, *args, **kwargs):
        users = User.objects.filter(*args, **kwargs)
        if not users.exists():
            raise ValidationError({
                'message': 'Ushbu parametrli account topilmadi'
            })
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attr):
        data = super(LoginRefreshSerializer, self).validate(attr)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance.get('user_id')
        user = get_object_or_404(User.objects.all(), id=user_id)
        update_last_login(None, user)
        return data


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_phone_number = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email_phone_number = data.get("email_phone_number")
        if not email_phone_number:
            raise ValidationError(
                {
                    "success": False,
                    'message': "Telefon raqamingiz yoki email manzilingizni kiritishingiz shart !"
                }
            )
        user = User.objects.filter(Q(email=email_phone_number) | Q(phone=email_phone_number))
        if not user.exists():
            raise NotFound("User not found")
        data['user'] = user.first()
        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Kiritgan parollaringiz bir-biriga teng emas"
                }
            )
        if password:
            validate_password(password)
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)
