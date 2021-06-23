from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser, SAFE_METHODS,
)
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
)
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.conf import settings
import pyotp
import jwt
import random
# end of django importing
# email
from django.core.mail import send_mail
from django.conf import settings
# project importing

from user.models import User
from user.serializers import (
    MainPasswordSerializer,
    CodeSendSerializer,
    CodeCheckSerializer,
    UserCreateSerializer,
    UserListSerializer,
    PasswordCodeSerializer,
    PasswordResetSerializer,
    PhoneNumberResetSerializer,
)
from user.utils import (
    send_code_to_phone_number,
    generate_correct_phone_number,
    is_phone_number_valid,
)


def generate_otp():
    totp = pyotp.TOTP(settings.OTP_SECRET_KEY, interval=120)
    code = totp.now()
    return code

class UserProfileApiView(APIView):
    permission_classes = [AllowAny,]

    def get(self, request, *args, **kwargs):
        user = request.user.id
        user = User.objects.filter(id=user).first()
        if not user:
            return Response({"err": "You have to enter your phone_number and password User not found!"},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserListSerializer(user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        ## in this endpoin, user can update its first_name and last_name
            by giving
            {
                "first_name":"someone",
                "last_name":"someonov"
            }
            in body
        """
        user = request.user.id
        obj = User.objects.filter(id=user).first()
        if obj is None:
            return Response({"err": "User not found!"},
                            status=status.HTTP_400_BAD_REQUEST)
        image = request.data.get("image", None)
        if image is not None:
            obj.image = image
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        if first_name is not None:
            obj.first_name = first_name
        if last_name is not None:
            obj.last_name = last_name
        obj.save(update_fields=["first_name", "last_name"])
        return Response({"user": UserListSerializer(obj).data},
                        status=status.HTTP_200_OK)


class CodeSendAPIView(APIView):
    """
    Send code to Phone
    # #send post to request to '''api/user/code/'''
    # to get code
    '''body{
        "phone_number"
    }'''
    """
    permission_class = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = CodeSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        code = generate_otp()
        phone_number = serializer.data.get("phone_number")

        payload = {
            "code": code,
            "phone_number": phone_number,
        }
        return Response(payload, status=status.HTTP_200_OK)


class CodeCheckAPIView(APIView):
    """
    check code which was send
    # # send post to request to '''api/user/check/'''
    # to get code
    '''body{
        "phone_number": "901766066",
        "code" : 23453,
    }'''
    """

    def post(self, request, *args, **kwargs):
        serializer = CodeCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.data.get("phone_number")
        token = jwt.encode({
            "new_user": phone_number,
            "rand_number": random.random()
        }, settings.OTP_SECRET_KEY, algorithm='HS256')
        return Response({
            "phone_number": phone_number,
            "token": token,
        }, status=status.HTTP_200_OK)


class UserPagePagination(PageNumberPagination):
    page_size = 10
    def generate_response(self, query_set, serializer_obj, request):
        try:
            page_date = self.paginat_queryset(query_set, request)
        except NotFound:
            return Response(
                {'errors': 'No resuls found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serialized_class = serializer_obj(page_date, many=True)
        return self.getpaginated_response(serialized_class.data)


class UserListCreateAPIView(ListCreateAPIView):
    """
    ## The endpoint where you can create new user
    #to create user, send POST request to ''' api/user/''' endpoint
    '''body{
        "phone_nmber": "9017766066",
        "firstname": "Bektosh",
        "last_name": "Salimov",
        "password": "123456",
        "token": ": "jbsdfkjasdhfafn.sdfghhjfd",
    }
    """

    queryset = get_user_model().objects.all().filter(is_superuser=False)
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny, ]
    pagination_class = UserPagePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserListSerializer
        elif self.request.method == 'POST':
            return UserCreateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [AllowAny, ]
        else:
            permission_classes = [IsAdminUser, ]
        return [permission() for permission in permission_classes]

    def post(self, request, *args, **kwards):
        data = request.data
        token = data.get('token', None)

        if not token:
            return Response({'error': 'Make sure you have included token'},
                            status=status.HTTP_400_BAD_REQUEST)

        payload = jwt.decode(
            token, settings.OTP_SECRET_KEY, algorithms=['HS256'])

        phone_number = data.get('phone_number')
        valid, msg = is_phone_number_valid(phone_number)

        if not valid:
            return Response({'error': 'Phone number is not valid'},
                            status=status.HTTP_400_BAD_REQUEST)

        c_p = generate_correct_phone_number(msg)
        if payload.get('new_user') != c_p:
            return Response({'error': 'Payload did not match'},
                            status=status.HTTP_400_BAD_REQUEST)
        serialized = UserCreateSerializer(data=data)
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        data = request.data
        serialized = PasswordResetSerializer(data=data)
        if serialized.is_valid():
            return Response({
                "msg": "Password changed successfully!"
            }, status=status.HTTP_200_OK)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordCodeAPIView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        data = request.data
        serialized = PasswordCodeSerializer(data=data)
        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        phone_number = serialized.data.get('phone_number')
        code = generate_otp()
        res = send_code_to_phone_number(code, phone_number, reset=True)
        payload = {
            "phone_number": phone_number,
            "code": code,
        }
        return Response(payload, status=status.HTTP_200_OK)


class PhoneNumberResetApiView(APIView):
    """
    json request format (with new phone number) {
        "phone_number" : "901766066",
        "token" : "sdfasdfasdf12312"
    }
    """
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        data = request.data
        data['old_phone_number'] = request.user.phone_number
        serialized = PhoneNumberResetSerializer(data=data)

        if not serialized.is_valid():
            return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response("The phone number was successfully changed", status=status.HTTP_200_OK)


def email(request):
    subject = 'Ro\'yxatdan o\'tganiz uchun rahmat'
    message = 'Haridingiz uchun rahmat!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['receiver@gmail.com',]
    send_mail( subject, message, email_from, recipient_list )
    return ('redirect to a new page')

