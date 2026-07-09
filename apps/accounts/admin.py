from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from hijack.contrib.admin import HijackUserAdminMixin
# Register your models here.


@admin.register(User)
class UserAdmin(HijackUserAdminMixin, UserAdmin):
    list_display = (
        'username',
        'name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
        'date_of_birth',
        'accepted_the_terms_of_use',
    )
    list_filter = ('is_staff', 'is_active', 'accepted_the_terms_of_use')
    search_fields = ('username', 'name', 'email')
    ordering = ('date_joined',)
