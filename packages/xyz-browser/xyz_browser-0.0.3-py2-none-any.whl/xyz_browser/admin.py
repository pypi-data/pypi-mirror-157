# -*- coding:utf-8 -*-
from __future__ import division
from __future__ import unicode_literals
from django.contrib import admin

from . import models, choices


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode', 'sender_type', 'is_active', 'create_time')
    search_fields = ("name", )
    date_hierarchy = 'create_time'



def reset_task_status(modeladmin, request, queryset):
    queryset.update(status=choices.STATUS_PENDING)


reset_task_status.short_description = "重置状态"

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('url', 'project', 'status', 'is_active', 'create_time', 'apply_time', 'finish_time')
    search_fields = ('url',)
    list_filter = ('status',)
    date_hierarchy = 'create_time'
    raw_id_fields = ('project', )
    actions = (reset_task_status, )
