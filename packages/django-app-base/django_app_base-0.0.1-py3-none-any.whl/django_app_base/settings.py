from django_app_base.custom_settings import CustomSettings

DEFAULTS = {
    'AUTH_PERMIT_PATH_LIST': [],
    'DEV_ENV': True,
    'AUTH_ACL': True
}

IMPORT_STRINGS = [

]


class DjangoAppBaseSettings(CustomSettings):
    pass


app_base_settings = DjangoAppBaseSettings(base_name='APP_BASE',
                                          defaults=DEFAULTS,
                                          import_strings=IMPORT_STRINGS)
