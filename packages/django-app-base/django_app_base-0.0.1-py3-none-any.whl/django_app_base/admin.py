from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, ContentType
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session
from django_app_base.models import *


@admin.register(User)
class MUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'phone', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions')

    list_display = ('id', 'username', 'name', 'phone', 'email', 'is_staff', 'is_active')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date')


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('app_label', 'model')
    search_fields = ('app_label', 'model')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    def app_model(self, obj):
        return "[%s] %s" % (obj.content_type.app_label, obj.content_type.name)

    app_model.short_description = 'app_model'

    list_display = ('name', 'codename', 'content_type', 'app_model')
    search_fields = ('name', 'codename')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_time', 'action_flag', 'user', 'content_type',
                    'object_repr')
