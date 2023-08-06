from rest_framework import serializers
from django_app_base.models import User
from django_app_base.serializers.permission import PermissionSimpleSerializer
from django_user_role.models import Role


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'username')


class RoleNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']


class UserInfoSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='auth_token.key', read_only=True)
    roles = RoleNameSerializer(source='role_set', many=True)
    user_permissions = PermissionSimpleSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'token', 'roles', 'user_permissions')
