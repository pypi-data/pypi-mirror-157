from rest_framework import serializers
from django_user_role.models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'desc', 'app_scope']
