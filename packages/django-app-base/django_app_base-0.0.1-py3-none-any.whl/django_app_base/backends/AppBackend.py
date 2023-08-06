from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model


class AppBackend:

    def _get_user_role_permissions(self, user_obj):
        return Permission.objects.filter(role__users=user_obj)

    def _get_group_role_permissions(self, user_obj):
        return Permission.objects.filter(role__user_groups__user=user_obj)

    def _get_department_role_permissions(self, user_obj):
        return Permission.objects.filter(role__department_role__users=user_obj)

    def _get_user_permissions(self, user_obj):
        return user_obj.user_permissions.all()

    def _get_group_permissions(self, user_obj):
        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

    def _get_permissions(self, user_obj, obj, from_name):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            setattr(user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
        return getattr(user_obj, perm_cache_name)

    def _get_role_permissions(self, user_obj, obj, from_name):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_role_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_role_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            setattr(user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
        return getattr(user_obj, perm_cache_name)

    def get_user_role_permissions(self, user_obj, obj=None):
        return self._get_role_permissions(user_obj, obj, 'user')

    def get_group_role_permissions(self, user_obj, obj=None):
        return self._get_role_permissions(user_obj, obj, 'group')

    def get_department_role_permissions(self, user_obj, obj=None):
        return self._get_role_permissions(user_obj, obj, 'department')

    def get_user_permissions(self, user_obj, obj=None):
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        return self._get_permissions(user_obj, obj, 'group')

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_role_perm_cache'):
            user_obj._role_perm_cache = {
                *self.get_user_permissions(user_obj),
                *self.get_group_permissions(user_obj),
                *self.get_user_role_permissions(user_obj),
                *self.get_group_role_permissions(user_obj),
                *self.get_department_role_permissions(user_obj)
            }
        return user_obj._role_perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_active and perm in self.get_all_permissions(user_obj, obj)

    def authenticate(self, request, username=None, password=None):
        return None
