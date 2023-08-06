# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals


def send_browse_done_event(task):
    from .signals import task_done
    sender = task.project.sender_type
    sender = sender.model_class() if sender else None
    task_done.send_robust(sender=sender, task=task)