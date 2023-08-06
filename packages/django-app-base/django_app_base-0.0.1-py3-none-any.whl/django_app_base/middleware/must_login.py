import logging
from django.contrib.auth import authenticate, login
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.conf import settings
from django_app_base.settings import app_base_settings

logger = logging.getLogger()


class MustLoginMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if app_base_settings.DEV_ENV == "dev" and not app_base_settings.AUTH_ACL:
            pass
        elif self.in_white_list(request):
            pass
        elif not request.user.is_authenticated:
            user = authenticate(request)
            if user:
                login(request, user)
            else:
                return self.forbidden(request)

    @staticmethod
    def forbidden(request):
        if request.is_ajax():
            logger.debug('no auth,request forbidden,request is ajax')
            return HttpResponseForbidden()
        else:
            logger.debug('no auth,request forbidden,request is not ajax')
            # return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
            return redirect(settings.LOGIN_URL)

    @staticmethod
    def in_white_list(request):
        for white_path in app_base_settings.AUTH_PERMIT_PATH_LIST:
            if request.path.startswith(white_path):
                return True

        return False
