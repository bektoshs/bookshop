from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


from user.models import (
    User,
)


'''
Following code is almost a boiler plate and it was just copied and pasted
I do not mean just Ctrl + C and Ctrl + V, I mean it is what was given in docs
it is has meanning only in Django's default admin site that'it
'''


class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password',
                           'first_name', 'last_name', 'email', 'paid_books'
                           )}),
        # (_('Personal Info'),{'fields': ('id', )}),
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff')
            }
        ),
        (_('Important Dates'), {
            'fields': ('last_login', )
        }),
    )
    add_fieldsets = (
        (None, {'classes': ('wide'),
                'fields': ('first_name',
                           'last_name',
                           'phone_number',
                           'email',
                           'password1',
                           'password2')
                }),
    )
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)



admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
