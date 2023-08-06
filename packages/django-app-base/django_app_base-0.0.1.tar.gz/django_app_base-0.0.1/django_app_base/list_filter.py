from datetime import date

from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class DeletedListFilter(admin.SimpleListFilter):
    title = _('是否删除')
    parameter_name = 'deleted'

    def lookups(self, request, model_admin):
        return (
            ('deleted', _('是')),
            ('using', _('否')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'deleted':
            # todo 暂未找到更改manager的方法,先使用此方法
            # return queryset.model.all_objects.filter(delete_time__gt=0)
            return queryset.filter(delete_time__gt=0)
        if self.value() == 'using':
            # return queryset.model.all_objects.filter(delete_time=0)
            return queryset.filter(delete_time=0)
