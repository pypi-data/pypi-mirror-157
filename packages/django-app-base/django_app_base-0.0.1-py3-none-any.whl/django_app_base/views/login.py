import json

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
import rest_framework.status as status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse

from django_app_base.serializers.user import UserSerializer
from django_app_base.utils.django_some import get_params

USE_TEMPLATE = settings.APP_CONFIG.USE_TEMPLATE


@api_view(['GET'])
def login_user(request):
    user = UserSerializer(request.user)
    return Response(data=user.data, status=status.HTTP_200_OK)


@csrf_exempt
@ensure_csrf_cookie
def login_view(request):
    params = get_params(request)

    if 'GET' == request.method:
        if USE_TEMPLATE:
            return render(request, 'index.html')
        else:
            return redirect("/")
    else:

        username = params.get('username', None)
        password = params.get('password', None)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if Token.objects.filter(user=request.user).exists():
                token_str = Token.objects.get(user=request.user).key
            else:
                token = Token.objects.create(user=request.user)
                token_str = token.key
            return JsonResponse(dict(token=token_str))
        else:
            return HttpResponse(None, None, 404)


def logout(request):
    django_logout(request)
    if 'GET' == request.method:
        if USE_TEMPLATE:
            return render(request, 'index.html')
        else:
            return redirect("/")
    else:
        return JsonResponse(data=dict(ok=True))


def index(request):
    if USE_TEMPLATE:
        return render(request, 'index.html')
    else:
        return redirect("/")
