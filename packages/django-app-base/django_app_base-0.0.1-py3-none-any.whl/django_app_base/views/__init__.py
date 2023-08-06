from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .permission_view import PermissionAdminView
from .user import UserView


@csrf_exempt
def health_check(request):
    return HttpResponse(None, None, 200)
