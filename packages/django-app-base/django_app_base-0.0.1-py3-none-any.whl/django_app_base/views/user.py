from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django_app_base.models import User
from django_app_base.serializers.user import UserSerializer, UserInfoSerializer, PermissionSimpleSerializer


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False)
    def info(self, request):
        user = request.user
        if user.is_authenticated:
            return Response(dict(
                code=20000,
                data={
                    'roles': ['admin'],
                    'introduction': '',
                    'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
                    'name': user.username
                },
            ))
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get', 'post'], detail=False, url_path='user_info')
    def get_user_info(self, request):
        user = request.user
        if user.is_authenticated:
            data = UserInfoSerializer(user).data
            return Response(data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get', ], detail=False, url_path='user_permissions')
    def get_user_permissions(self, request):
        user = request.user
        queryset = user.user_permissions.all()
        return Response(PermissionSimpleSerializer(queryset, many=True).data)

    @action(methods=['get'], detail=False)
    def count(self, request):
        count = User.objects.count()
        return Response(dict(count=count))
