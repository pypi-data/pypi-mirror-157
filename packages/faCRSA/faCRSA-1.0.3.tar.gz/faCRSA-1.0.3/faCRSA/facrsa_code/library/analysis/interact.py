#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Author: Ruinan Zhang
Version: v1.2
LastEditTime: 2022-07-01 09:35:26
E-mail: 2020801253@stu.njau.edu.cn
Copyright (c) 2022 by Ruinan Zhang, All Rights Reserved. Licensed under the GPL v3.0.
'''
from facrsa_code.library.util.sqliteUtil import sqliteUtil
import zipfile
import os
from pathlib import Path


class interact():
    def __init__(self, uid, tid, type):
        self.uid = str(uid)
        self.tid = str(tid)
        self.info = self.get_task_info()

    def get_task_info(self):
        sql = 'select * from task where tid ="' + str(self.tid) + '"' + ' and uid ="' + str(self.uid) + '"'
        res = sqliteUtil().fetch_one(sql)
        return res

    def re_img_name(self, folder_str):
        """
        恢复上传到cos文件的名字
        :param folder_str:
        :return:
        """
        filelist = os.listdir(folder_str + "initial")
        for img in filelist:
            with sqliteUtil() as um:
                sql = 'SELECT image FROM result WHERE re_img = ' + '"' + img + '"' + 'and tid=' + self.tid
                res = um.fetch_one(sql)
            original = folder_str + "initial/" + img
            rename = folder_str + "initial/" + res['image']
            os.rename(original, rename)

    def initial_analysis(self):
        factor = self.info['factor']
        mail = self.info['email']
        private_plugin = self.info['private_plugin']

        # # download private plugin
        # if str(private_plugin) != '0':
        #     with sqliteUtil() as um:
        #         # 检索当前任务对应的自定义插件
        #         sql = 'SELECT pid FROM plugin WHERE tid=' + str(self.tid)
        #         res = um.fetch_one(sql)
        #     # todo 根据数据库信息修改预测时的插件路径
        #
        # 解压并重命名文件
        # process_type：单张（多张）/zip压缩包
        # if self.process_type == 1:
        #     file = self.folder_str + self.tid + ".zip"
        #     fz = zipfile.ZipFile(file, 'r')
        #     for file in fz.namelist():
        #         fz.extract(file, self.folder_str + "initial")

        return factor, mail, private_plugin
