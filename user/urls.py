from django.urls import path, include
from rest_framework.routers import SimpleRouter
from user.views import (
    UserListCreateAPIView,
    CodeSendAPIView,
    CodeCheckAPIView,
    UserProfileApiView,
    PasswordCodeAPIView,
    PasswordResetAPIView,
    PhoneNumberResetApiView,
)

router = SimpleRouter()



urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='user-list-create'),
    path('profile/', UserProfileApiView.as_view(), name='user-profile'),
    path('send/code/', CodeSendAPIView.as_view(), name='code_send_phone'),
    path('check/code/', CodeCheckAPIView.as_view(), name='check-code'),
    path('password/code/', PasswordCodeAPIView.as_view(), name='password-code'),
    path('password/reset/', PasswordResetAPIView.as_view(), name='password-reset'),
    path('phonenumber/reset/', PhoneNumberResetApiView.as_view(), name='phone_number-reset')
]
