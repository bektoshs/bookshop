from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from user.utils import validate_phone_number_or_email
from book.models import Book


class UserManager(BaseUserManager):
    """User Manager class for custom user"""

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Users must have a phone number!")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        user = self.create_user(phone_number, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user



class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=20, unique = True)
    phone_number = models.CharField(max_length=20, unique = True, validators=[
                                    RegexValidator(regex=r'^(\+?998)?([. \-])?((\d){2})([. \-])?(\d){3}([. \-])?(\d){2}([. \-])?(\d){2}$',
                                                   message="Given phone number \
                                                   is not valid")])
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    paid_books = models.ManyToManyField(Book, blank=True, related_name='paid_book')
    objects = UserManager()
    USERNAME_FIELD = 'phone_number'

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return '{} {} {}'.format(self.first_name, self.last_name, self.phone_number)

