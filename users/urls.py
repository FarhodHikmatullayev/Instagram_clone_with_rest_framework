from django.urls import path
from .views import CreateUserApiView, VerifyApiView, GetNewVerificationApiVie, ChangeUserInformationApiView, \
    ChangeUserPhotoApiView, LoginApiView, LoginRefreshApiView, LogOutApiView, ForgotPasswordApiView, \
    ResetPasswordApiView

app_name = 'users'

urlpatterns = [
    path('login/', LoginApiView.as_view(), name='login'),
    path('login/refresh/', LoginRefreshApiView.as_view(), name='login_refresh'),
    path('logout/', LogOutApiView.as_view(), name='logout'),
    path('signup/', CreateUserApiView.as_view(), name='signup'),
    path('verify/', VerifyApiView.as_view(), name='verify'),
    path('new-verify/', GetNewVerificationApiVie.as_view(), name='new_verify'),
    path('change-user/', ChangeUserInformationApiView.as_view(), name='change_user'),
    path('change-user-photo/', ChangeUserPhotoApiView.as_view(), name='change_user_photo'),
    path('forgot-password/', ForgotPasswordApiView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordApiView.as_view(), name='forgot_password'),
]
