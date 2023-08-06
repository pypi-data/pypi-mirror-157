# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from xyz_util.modelutils import JSONField
from . import choices
from django.contrib.contenttypes.models import ContentType

class Project(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "项目"
        ordering = ('-create_time',)
        unique_together = ('name', 'sender_type')

    name = models.CharField("名称", max_length=64, db_index=True)
    sender_type = models.ForeignKey(ContentType, verbose_name='发起者', blank=True, null=True,
                                    related_name='browser_projects', on_delete=models.PROTECT)
    mode = models.PositiveSmallIntegerField('模式', blank=True, default=choices.MODE_PC,
                                              choices=choices.CHOICES_MODE)
    script = models.TextField("脚本", blank=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    is_active = models.BooleanField("有效", blank=False, default=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "任务"
        ordering = ('-create_time',)

    project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name,
                                related_name='tasks', on_delete=models.PROTECT)
    url = models.URLField('URL地址', max_length=255, db_index=True)
    status = models.PositiveSmallIntegerField('状态', blank=True, default=choices.STATUS_PENDING,
                                              choices=choices.CHOICES_STATUS, db_index=True)
    data = JSONField('数据', blank=True, default={})
    is_active = models.BooleanField("有效", blank=False, default=True)
    salt = models.CharField("加密盐", max_length=6, blank=False, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)
    apply_time = models.DateTimeField('申请时间', blank=True, null=True)
    finish_time = models.DateTimeField('结束时间', blank=True, null=True)

    def __str__(self):
        return '%s(%s)' % (self.project, self.url)
