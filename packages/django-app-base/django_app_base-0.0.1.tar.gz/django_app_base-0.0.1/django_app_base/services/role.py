from simple_common.local import local
from collections import defaultdict


class RoleService(object):

    @staticmethod
    def get_perm_names_on_user(user):
        """
        从django的permission表中获取所有的permission
        :param user:
        :return:
        """
        perms = user.user_permissions.all().values_list('content_type__app_label', 'codename', 'name').order_by()
        return [["%s.%s" % (ct, codename), name] for ct, codename, name in perms]

    @staticmethod
    def get_perm_names_on_group(group):
        """
        从django的group获取相关的permission
        :param group:
        :return:
        """
        perms = group.permissions.all().values_list('content_type__app_label', 'codename', 'name').order_by()
        return [["%s.%s" % (ct, codename), name] for ct, codename, name in perms]

    @staticmethod
    def get_perm_names_on_role(role):
        """
        获取某个role的permission
        :param role:
        :return:
        """
        perms = role.permissions.all().values_list('content_type__app_label', 'codename', 'name').order_by()
        return [["%s.%s" % (ct, codename), name] for ct, codename, name in perms]

    @staticmethod
    def get_perm_names_on_department_role(department):
        """
        获取某个department的permission
        一个department可能有多个role
        :param department:
        :return:
        """
        pass

    @staticmethod
    def my_tree():
        user = local.user
        user_perms = RoleService.get_perm_names_on_user(user)
        permission_map = dict(
            user=list(user_perms),
            group=dict(),
            role=dict(),
            department=defaultdict(dict),
        )

        for role in user.role_set.all():
            # 获取每个role上面的permission
            permission_map['role'][role.name] = list(RoleService.get_perm_names_on_role(role))

        for group in user.groups.all():
            permission_map['group'][group.name] = list(RoleService.get_perm_names_on_role(group))

        if user.department:
            for role in user.department.roles.all():
                permission_map['department'][user.department.name][role.name] = list(
                    RoleService.get_perm_names_on_role(role))

        return permission_map
