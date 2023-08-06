import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django_app_base.settings import app_base_settings

logger = logging.getLogger()


class PermitUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if app_base_settings.DEV_ENV == "dev" and not app_base_settings.AUTH_ACL:
            pass
        elif self.in_white_list(request):
            pass
        elif request.user.is_superuser:
            pass
        else:
            flag = False
            for group in request.user.groups.all():
                if group.name == 'white_user':
                    flag = True
                    break
            if flag:
                pass
            else:
                logger.info('WhiteUserMiddleware Forbidden!')
                return HttpResponseForbidden()

    @staticmethod
    def in_white_list(request):
        for white_path in app_base_settings.AUTH_PERMIT_PATH_LIST:
            if request.path.startswith(white_path):
                return True

        return False
