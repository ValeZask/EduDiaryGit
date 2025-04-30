from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профили'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'role', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'role')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)
    inlines = (ProfileInline,)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('username', 'full_name', 'role', 'avatar')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_number', 'class_letter', 'phone')
    search_fields = ('user__email', 'user__full_name', 'phone')
    list_filter = ('class_number',)
