# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class ProjectSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Project
        exclude = ()


class TaskSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    project_name = serializers.CharField(label='项目', source='project', read_only=True)

    class Meta:
        model = models.Task
        exclude = ('salt',)


class TaskFullSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = models.Task
        exclude = ()
