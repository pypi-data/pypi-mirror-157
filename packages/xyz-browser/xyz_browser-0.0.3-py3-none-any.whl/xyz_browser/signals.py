# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import Signal

task_done = Signal(providing_args=["task"])

to_create_task = Signal(providing_args=["project", "url"])
to_create_project = Signal(providing_args=["name", "mode", "script", "sender"])
