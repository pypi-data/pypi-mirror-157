from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework.decorators import action

from django.contrib.auth.models import Permission
from django_app_base.serializers import PermissionSimpleSerializer


class PermissionAdminView(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSimpleSerializer

    @action(methods=['get'], detail=False,
            serializer_class=PermissionSimpleSerializer)
    def my_permission(self, request):
        # 仅可访问自己有什么权限
        user = request.user
        serializer_class = self.get_serializer_class()
        serializer = serializer_class()
        data = serializer(user.user_permissions.all(), many=True).data
        return Response(data)

    @action(methods=['get'], detail=False)
    def count(self, request):
        count = Permission.objects.count()
        return Response(dict(count=count))
