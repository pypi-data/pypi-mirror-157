from django.conf import settings


def get_prod_env():
    return getattr(settings, 'DAB_PROD_ENV', 'dev')


def get_auth_acl():
    return getattr(settings, 'DAB_AUTH_ACL', True)


def get_auth_permit_user_list():
    return getattr(settings, 'DAB_AUTH_PERMIT_USER_LIST', [])
