from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']

    # Modify the included fields
    # Without this, the admin page to edit user will not be accessible.

    # Define your custom fieldsets
    fieldsets = (
        # Title  #Fields
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        )
    )

    readonly_fields = ['last_login']

    # Customise add user page in order to make it accessible
    # after modifying auth user model.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    exclude = ['username', 'first_name', 'last_name', 'date_joined']

# Register your models here.
admin.site.register(User, UserAdmin)

