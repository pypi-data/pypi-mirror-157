from django.apps import AppConfig


class AppBaseConfig(AppConfig):
    name = 'django_app_base'

    def ready(self):
        from .signals import receiver
