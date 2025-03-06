from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    커스텀 사용자 관리자 설정
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'profile_image', 'bio')}),
        (_('Skill info'), {'fields': ('skill_level', 'rating')}),
        (_('Match stats'), {'fields': ('matches_played', 'wins', 'draws', 'losses')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'skill_level', 'rating', 'matches_played', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'skill_level')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)
