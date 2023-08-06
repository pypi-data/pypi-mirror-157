# -*- coding:utf-8 -*-
from __future__ import print_function
from django.dispatch import receiver
from . import signals, models, choices
import logging
from django.utils.crypto import get_random_string

log = logging.getLogger('django')


@receiver(signals.to_create_task)
def create_task(sender, **kwargs):
    project = kwargs['project']
    url = kwargs['url']
    platform, created = project.tasks.get_or_create(
        url=url,
        status=choices.STATUS_PENDING,
        defaults=dict(
            salt=get_random_string(6)
        )
    )


@receiver(signals.to_create_project)
def create_project(sender, **kwargs):
    from django.contrib.contenttypes.models import ContentType
    project, created = models.Project.objects.get_or_create(
        name=kwargs['name'],
        sender_type=ContentType.objects.get_for_model(sender) if sender else None,
        defaults=dict(
            mode=kwargs.get('mode', choices.MODE_PC),
            script=kwargs['script']
        )
    )
    return project
