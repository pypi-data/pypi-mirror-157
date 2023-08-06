from datetime import datetime
from enum import Enum, EnumMeta
from django.db import models
from simple_common.local import local
from django.conf import settings


class ModelBase(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)
    date_modify = models.DateTimeField(auto_now=True)

    user_create = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name="%(app_label)s_%(class)s_user_create",
                                    related_query_name="%(app_label)s_%(class)s_user_create",
                                    null=True, blank=True)

    user_modify = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name="%(app_label)s_%(class)s_user_modify",
                                    related_query_name="%(app_label)s_%(class)s_user_modify",
                                    null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.user_create:
            if hasattr(local, 'user') and local.user.is_authenticated:
                self.user_create = local.user

        if not self.user_modify:
            if hasattr(local, 'user') and local.user.is_authenticated:
                self.user_modify = local.user

        if kwargs.get('update_modify_user', False):
            self.user_modify = local.user

        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['-date_create']


class FilterDeleteManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().order_by('-date_create')

    def filter_used(self):
        return self.get_queryset().filter(delete_time=0)

    def filter_deleted(self):
        return self.get_queryset().filter(delete_time__gt=0)


class DModelBase(ModelBase):
    delete_time = models.IntegerField(default=0)
    user_delete = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name="%(app_label)s_%(class)s_user_delete",
                                    related_query_name="%(app_label)s_%(class)s_user_delete",
                                    null=True, blank=True)

    objects = FilterDeleteManager()

    def delete(self, using=None, keep_parents=False, delete=True):
        if delete:
            return super().delete()
        else:
            now = datetime.now()
            self.delete_time = int(now.timestamp())
            self.save(update_fields=['delete_time'])
            # todo return value

    def real_delete(self, using=None, keep_parents=False):
        return self.delete(using, keep_parents, delete=True)

    def fake_delete(self, using=None, keep_parents=False):
        return self.delete(using, keep_parents, delete=False)

    class Meta:
        abstract = True
        ordering = ['-date_create']


class ChoiceEnumMeta(EnumMeta):
    def __iter__(self):
        return ((tag.name, tag.value) for tag in super().__iter__())


class ScopeTypeChoice(Enum, metaclass=ChoiceEnumMeta):
    mine_scope = 'my scope'
    mine_public_scope = 'mine can share scope'
    department_scope = 'department scope'
    department_public_scope = 'share in department'
    global_scope = 'global scope'

    def __call__(self, *args, **kwargs):
        return self.name
