import os
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth.mixins import PermissionRequiredMixin

from django_app_base.services import RoleService
from django_app_base.common import SuccessJsonResponse

from django_user_role.models import Role
from django_app_base.serializers import RoleSerializer


class RoleAdminView(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @action(methods=['get'], detail=False)
    def count(self, request):
        count = Role.objects.count()
        return Response(dict(count=count))

    @action(methods=['get'], detail=False)
    def my_tree(self, request):
        result = RoleService.my_tree()
        return Response(result)
