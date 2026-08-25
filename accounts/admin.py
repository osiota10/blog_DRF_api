from django.contrib import admin

from . models import *
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount
from .forms import UserChangeForm, UserCreationForm


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('email',)
    list_display = ('first_name', 'last_name', 'email',
                    'account_type', 'is_active', 'is_staff', 'is_superuser')
    model = UserAccount
    fieldsets = (
        (None, {'fields': ('profile_picture', 'password',)}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'gender', 'phone_number', 'date_of_birth', 'account_type')}),
        ('Contact Address', {
         'fields': ('home_address', 'local_govt', 'state_of_origin', 'nationality',)}),
        ('Permissions', {
         'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {
            'fields': ('date_joined', 'last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')}
         ),
    )


admin.site.register(UserAccount, CustomUserAdmin)
