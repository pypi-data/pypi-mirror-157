from django.db import models
from django.contrib.auth.models import Permission, Group
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from django_app_base.models.base import ModelBase


class Department(ModelBase):
    # 部门名称,可以重名
    name = models.CharField(max_length=50, db_index=True)
    # 标识一共有多少层,包括当前层
    level_num = models.IntegerField()
    user_group = models.OneToOneField(Group, on_delete=models.SET_NULL, null=True, blank=True)
    level_0 = models.CharField(max_length=50)
    level_1 = models.CharField(max_length=50, null=True, blank=True)
    level_2 = models.CharField(max_length=50, null=True, blank=True)
    level_3 = models.CharField(max_length=50, null=True, blank=True)
    level_4 = models.CharField(max_length=50, null=True, blank=True)
    level_5 = models.CharField(max_length=50, null=True, blank=True)
    level_6 = models.CharField(max_length=50, null=True, blank=True)
    level_7 = models.CharField(max_length=50, null=True, blank=True)
    level_8 = models.CharField(max_length=50, null=True, blank=True)
    level_9 = models.CharField(max_length=50, null=True, blank=True)

    roles = models.ManyToManyField('django_user_role.Role',
                                   related_name='department_role',
                                   related_query_name='department_role',
                                   blank=True)

    def __str__(self):
        temp = []
        for i in range(self.level_num):
            temp.append(str(getattr(self, 'level_%d' % i)))
        return "%s %s" % (self.name, ('/' + '/'.join(temp)))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['level_0',
                                            'level_1',
                                            'level_2',
                                            'level_3',
                                            'level_4',
                                            'level_5',
                                            'level_6',
                                            'level_7',
                                            'level_8',
                                            'level_9'], name='unique_level'),
        ]

    def set_parent_level(self, levels):
        # 不包括当前
        for i, v in enumerate(levels):
            setattr(self, 'level_%d' % i, v)
        self.level_num = len(levels) + 1

    def set_all_level(self, levels):
        # 包括当前
        for i, v in enumerate(levels):
            setattr(self, 'level_%d' % i, v)
        self.level_num = len(levels)
        self.name = levels[-1]

    @staticmethod
    def refresh_department(levels):
        """
        :param levels: 全路径,包括当前路径
        :return:
        """
        # q = Q()
        temp = {}
        for i, v in enumerate(levels):
            temp['level_%d' % i] = v

            # q = q & Q(**temp)
        # q = q & Q(level_num=len(levels))
        temp['level_num'] = len(levels)
        temp['name'] = levels[-1]
        d, created = Department.objects.get_or_create(**temp)
        return d, created
