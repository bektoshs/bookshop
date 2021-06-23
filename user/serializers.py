from book.serializers import BookListSerializer
from rest_framework.fields import IntegerField
from rest_framework.serializers import (
    SerializerMethodField,
    ModelSerializer,
    Serializer,
    CharField,
)

from django.core.validators import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
import pyotp
import jwt
import random
from datetime import datetime
from user.models import User
from user.utils import (
    generate_correct_phone_number,
    is_phone_number_valid,
    is_status_paid,
    is_email
)


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password',
                  'phone_number', 'email',)

        read_only_fields = ('id',)

        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
                'style': {
                    'input_type': 'password'
                }
            }
        }

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        valid, msg = is_phone_number_valid(phone_number)

        if not valid:
            raise ValidationError(msg)
        user = get_user_model().objects.filter(phone_number=phone_number)
        if user:
            raise ValidationError(
                'A user with the given phone number already exists')
        user = get_user_model().objects.create_user(**validated_data)

        return user


class MainPasswordSerializer(Serializer):
    @staticmethod
    def validate_phone_number_exists(phone_number):
        user = get_user_model().objects.filter(phone_number=phone_number).first()
        if not user:
            raise ValidationError('User with the given number was not found!')
        return user


class CodeSendSerializer(MainPasswordSerializer):
    phone_number = CharField(max_length=255)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        valid, msg = is_phone_number_valid(phone_number)
        if not valid:
            raise ValidationError(msg)
        self.validate_phone_number_exists(phone_number)
        phone_number = generate_correct_phone_number(phone_number)
        attrs['phone_number'] = phone_number
        return attrs

    @staticmethod
    def validate_phone_number_exists(phone_number):
        user_qs = get_user_model().objects.filter(phone_number=phone_number)
        if user_qs:
            raise ValidationError('user with the given number already exists!')


class CodeCheckSerializer(Serializer):
    code = CharField(max_length=255)
    phone_number = CharField(max_length=255)

    def validate(self, attrs):
        code = attrs.get('code', None)
        phone_number = attrs.get('phone_number')
        if not phone_number or not code:
            raise ValidationError('Phone number and code are required!')
        valid, msg = is_phone_number_valid(phone_number)
        if not valid:
            raise ValidationError(msg)
        self.validate_otp_code(code)

        return attrs

    @staticmethod
    def validate_otp_code(code):
        totp = pyotp.TOTP(settings.OTP_SECRET_KEY, interval=120)  # needed?
        res = totp.verify(code, valid_window=3)
        if res is False:
            raise ValidationError('code did not match')
        return True


class PasswordResetSerializer(MainPasswordSerializer):
    token = CharField(write_only=True)
    phone_number = CharField(write_only=True, max_length=255)
    password = CharField(write_only=True, max_length=255)

    def validate(self, attrs):
        token = attrs.get('token')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        if not phone_number or not token or not password:
            raise ValidationError(
                'Token, phone numer and password are required!')
        if len(password) < 5:
            raise ValidationError('Password length must be at least 5 chars!')
        valid, msg = is_phone_number_valid(phone_number)
        if not valid:
            raise ValidationError('Phone number is not valid!')
        user = self.validate_phone_number_exists(phone_number)
        c_p = generate_correct_phone_number(msg)
        self.validate_custom_token(token, c_p)  # +998 ??? to phone number
        self.save_user_password(user, password)
        return attrs

    @staticmethod
    def save_user_password(user, password):
        user.set_password(password)
        user.save()

    @staticmethod
    def validate_custom_token(token, phone_number):
        if not token:
            raise ValueError('Token is required!')

        try:
            payload = jwt.decode(
                token, settings.OTP_SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            raise ValidationError(str(e))

        if payload.get('new_user') != phone_number:
            raise ValidationError('payload did not match!')
        return token


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone_number", "paid_books")


class PasswordCodeSerializer(MainPasswordSerializer):
    phone_number = CharField(max_length=255)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        valid, msg = is_phone_number_valid(phone_number)
        if not valid:
            raise ValueError('phone number is not valid!')
        self.validate_phone_number_exists(phone_number)
        c_p = generate_correct_phone_number(msg)
        attrs['phone_number'] = c_p
        return attrs


class PhoneNumberResetSerializer(Serializer):
    token = CharField(write_only=True)
    phone_number = CharField(write_only=True, max_length=255)
    old_phone_number = CharField(write_only=True, max_length=255)

    def validate(self, attrs):
        token = attrs.get('token', None)
        new_pn = attrs.get('phone_number', None)
        old_pn = attrs.get('old_phone_number', None)

        # takes old phone number from header
        if not old_pn:
            raise ValidationError(
                "A User must be registered before changing the password")

        flag, new_pn = is_phone_number_valid(new_pn)
        if not flag:
            raise ValidationError(new_pn)
        cp = generate_correct_phone_number(new_pn) # +998 ???
        # new phone number is used since it received the code
        self.validate_custom_token(token, new_pn)
        self.save_new_phone_number(old_pn, cp)
        return attrs

    @staticmethod
    def validate_custom_token(token, phone_number):
        if not token:
            raise ValueError('Token is required!')

        try:
            payload = jwt.decode(
                token, settings.OTP_SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            raise ValidationError(str(e))

        if payload.get('new_user') != phone_number:
            raise ValidationError('payload did not match!')
        return token

    @staticmethod
    def save_new_phone_number(old_num, new_num):
        user = get_user_model().objects.filter(phone_number=old_num)[0]
        user.phone_number = new_num
        user.save()
