#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Author: Ruinan Zhang
Version: v1.2
LastEditTime: 2022-07-01 11:13:36
E-mail: 2020801253@stu.njau.edu.cn
Copyright (c) 2022 by Ruinan Zhang, All Rights Reserved. Licensed under the GPL v3.0.
'''
import subprocess
import click
import os

@click.command()
def start_queue():
    current_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_path)
    cmd = "python huey_consumer.py task_queue.huey"
    subprocess.call(cmd, shell=True)
