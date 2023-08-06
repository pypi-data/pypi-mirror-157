from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import authenticate, login

from django.views.decorators.csrf import csrf_exempt


class AuthenticationMiddleware(MiddlewareMixin):

    @csrf_exempt
    def process_request(self, request):
        # after django auth, user may be anonymous
        if getattr(request, 'user', None):
            if request.user.is_authenticated:
                pass
            else:
                if request.META.get("HTTP_AUTHORIZATION", None):
                    user = authenticate(request)
                    if user:
                        login(request, user)
                    else:
                        pass
        else:
            if request.META.get("HTTP_AUTHORIZATION", None):
                user = authenticate(request)
                if user:
                    login(request, user)
                else:
                    pass
            else:
                pass
