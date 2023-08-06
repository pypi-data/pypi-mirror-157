#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Author: Ruinan Zhang
Version: v1.2
LastEditTime: 2022-07-01 12:05:33
E-mail: 2020801253@stu.njau.edu.cn
Copyright (c) 2022 by Ruinan Zhang, All Rights Reserved. Licensed under the GPL v3.0.
'''
from task_queue import huey


@huey.task()
def submit_task(uid, tid):
    web_action(uid, tid)
    return tid


from facrsa_code.library.analysis.main import web_action
