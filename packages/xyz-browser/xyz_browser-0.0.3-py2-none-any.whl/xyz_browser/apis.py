# -*- coding:utf-8 -*-
from __future__ import division

from xyz_restful.mixins import BatchActionMixin
from . import models, serializers, choices, helper
from rest_framework import viewsets, decorators, response, exceptions
from xyz_restful.decorators import register
from datetime import datetime
from django.utils.crypto import get_random_string

@register()
class ProjectViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    search_fields = ('name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'mode': ['in', 'exact'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'name', 'create_time')


@register()
class TaskViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    search_fields = ('name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'project': ['in', 'exact'],
        'status': ['in', 'exact'],
        'is_active': ['exact'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'name', 'create_time')



    @decorators.action(['PATCH'], detail=False)
    def apply(self, request):
        qset = self.filter_queryset(self.get_queryset())
        a = qset.filter(status=choices.STATUS_PENDING).first()
        rs = []
        if a:
            a.status = choices.STATUS_RUNNING
            a.apply_time = datetime.now()
            a.salt = get_random_string(6)
            a.save()
            rs = [serializers.TaskFullSerializer(a).data]
        return response.Response(rs)


    @decorators.action(['PATCH'], detail=True, permission_classes=[])
    def report(self, request, pk):
        task = self.get_object()
        rd = request.data
        if rd.get('salt') != task.salt:
            raise exceptions.PermissionDenied('验证码不正确。')
        task.data = rd['data']
        task.finish_time = datetime.now()
        task.status = choices.STATUS_SUCCESS
        task.save()
        helper.send_browse_done_event(task)
        return response.Response(serializers.TaskSerializer(task).data)