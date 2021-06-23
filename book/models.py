from django.db import models
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4
import os


def image_path(instance, filename):
    ext = str(filename).split('.')[-1]
    filename = f"{uuid4()}.{ext}"
    return os.path.join('upload/books', filename)


class Category(models.Model):
    name = models.CharField(_('Category'), max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    cost = models.PositiveIntegerField(default=0)
    image = models.ImageField(blank = True, null = True, upload_to=image_path)
    printed_data = models.DateTimeField(_('Printed date: '), blank=True, null=True)

    def __str__(self):
        return self.title





