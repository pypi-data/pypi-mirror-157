from django.utils.deprecation import MiddlewareMixin

from simple_common.local import local


class LocalMiddleware(MiddlewareMixin):

    def process_request(self, request):
        self.set_local(request)

    def set_local(self, request):
        user = getattr(request, 'user', None)
        local.user = user
