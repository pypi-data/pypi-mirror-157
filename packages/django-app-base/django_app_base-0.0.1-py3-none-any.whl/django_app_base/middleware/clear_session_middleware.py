import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger()


class AuthAclMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        try:
            if request.session.get("is_api_token_request", False):
                request.session.flush()
        except Exception as e:
            logger.error('clear session middleware failed', exc_info=e)
        return response
