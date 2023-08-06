from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

__all__ = ['User']


class User(AbstractUser):
    username = models.CharField(
        max_length=128, unique=True, verbose_name=_('Username')
    )

    name = models.CharField(max_length=128, verbose_name=_('Name'))

    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_('Phone')
    )

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', None)
        if len(kwargs.keys()) == 1 and update_fields:
            try:
                super().save(*args, **kwargs)
            except Exception as e:
                # 当数据库只读时此字段无法修改,但是让用户可以登录是合理的
                print(e)
                pass
        else:
            super().save(*args, **kwargs)

    def has_role(self, role_name):
        return role_name in [value[0] for value in self.roles.all().values_list('name')]

    def get_all_role_names(self):
        return [role.name for role in self.role_set.all()]
