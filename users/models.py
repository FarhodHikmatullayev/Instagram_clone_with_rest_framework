import uuid
from datetime import datetime, timedelta
from random import randint

from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel

ORDINARY, MANAGER, ADMIN = 'ordinary', 'manager', 'admin'
VIA_EMAIL, VIA_PHONE = 'via_email', 'via_phone'
NEW, CODE, DONE, PHOTO = 'new', 'code', 'done', 'photo'


class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY, ORDINARY),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )
    AUTH_TYPES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE, CODE),
        (DONE, DONE),
        (PHOTO, PHOTO),
    )
    user_role = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPES)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=13, null=True, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True,
                              validators=[
                                  FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'heif', 'heic'])])

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, verify_type):
        code = "".join([str(randint(1, 10) % 10) for i in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            code=code,
            verify_type=verify_type
        )
        return code

    def __str__(self):
        return self.username

    def check_username(self):
        if not self.username:
            tem_username = f"username-{uuid.uuid4().__str__().split('-')[-1]}"
            print(tem_username)
            while User.objects.filter(username=tem_username):
                tem_username = f"{tem_username}{randint(1, 9)}"
            self.username = tem_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email
        elif self.email == "":
            self.email = None

    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh_token': str(refresh)
        }

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()
        self.hashing_password()

    def save(self, *args, **kwargs):
        print('id', self.id)
        self.clean()
        super(User, self).save(*args, **kwargs)


EXPIRE_EMAIL = 5
EXPIRE_PHONE = 2


class UserConfirmation(BaseModel):
    VERIFY_TYPES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=31, choices=VERIFY_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confirmation')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EXPIRE_EMAIL)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=EXPIRE_PHONE)
        super(UserConfirmation, self).save(*args, **kwargs)
