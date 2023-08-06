# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
 
MODE_PC = 1
MODE_MOBILE = 2

CHOICES_MODE = (
    (MODE_PC, '电脑'),
    (MODE_MOBILE, '手机'),
)

STATUS_PENDING = 0
STATUS_RUNNING = 1
STATUS_SUCCESS = 2
STATUS_OBSOLETE = 4

CHOICES_STATUS = (
    (STATUS_PENDING, '等待'),
    (STATUS_RUNNING, '执行中'),
    (STATUS_SUCCESS, '成功'),
    (STATUS_OBSOLETE, '放弃'),
)
