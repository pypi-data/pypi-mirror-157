import re
import collections
from django.contrib.auth import get_user_model


def get_admin():
    return get_user_model.objects.get(username='admin')


def user_is_authenticated(user):
    if isinstance(user.is_authenticated, collections.Callable):
        authenticated = user.is_authenticated()
    else:
        authenticated = user.is_authenticated

    return authenticated
