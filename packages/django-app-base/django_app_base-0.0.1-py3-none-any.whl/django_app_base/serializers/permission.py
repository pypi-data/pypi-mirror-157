from rest_framework import serializers
from django.contrib.auth.models import Permission


class PermissionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('codename',)
