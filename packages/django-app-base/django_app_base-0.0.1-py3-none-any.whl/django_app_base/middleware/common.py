from django.utils.deprecation import MiddlewareMixin

from simple_common.utils.string_utils import str_contain_some


class CommonMiddleware(MiddlewareMixin):
    def process_request(self, request):

        setattr(request, '_dont_enforce_csrf_checks', True)

        if self.is_from_browser(request):
            setattr(request, 'origin_type', 'browser')
        else:
            setattr(request, 'origin_type', 'api')

    @staticmethod
    def is_from_browser(request):
        user_agent = request.META.get('HTTP_USER_AGENT', None)
        if user_agent:
            return str_contain_some(user_agent.lower(), 'mozilla', 'applewebkit', 'chrome', 'safari')
        else:
            return False
