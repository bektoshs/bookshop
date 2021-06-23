from django.contrib import admin
from book.models import (
    Book,
    Category,
)

# class BookInline(admin.TabularInline):
#     model = Book
#     extra = 1

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     inlines = [BookInline, ]

admin.site.register(Category)
admin.site.register(Book)
