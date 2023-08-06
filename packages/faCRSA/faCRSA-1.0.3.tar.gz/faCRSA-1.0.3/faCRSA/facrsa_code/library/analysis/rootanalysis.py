#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Author: Ruinan Zhang
Version: v1.2
LastEditTime: 2022-07-01 09:36:20
E-mail: 2020801253@stu.njau.edu.cn
Copyright (c) 2022 by Ruinan Zhang, All Rights Reserved. Licensed under the GPL v3.0.
"""
import cv2 as cv
import numpy as np
from skimage import measure
import pandas as pd
import math
from skimage.morphology import convex_hull_image, skeletonize
from facrsa_code.library.analysis.database.writermysql import update_schedule, update_task_error
from facrsa_code.library.analysis.errorcheck import send_mail_user


class rootAnalysis():
    def __init__(self, img_list, conf, file_array, tid):
        self.conf = conf
        self.tid = tid
        self.df = pd.DataFrame(
            columns=["Image_Name", "Total_Root_Length(cm)", "Total_Root_Projected_Area(cm2)",
                     'Total_Surface_Area(cm2)',
                     'Total_Root_Volume(cm3)', "Primary_Root_Length(cm)", "Primary_Root_Projected_Area(cm2)",
                     "Primary_Root_Surface_Area(cm2)", "Primary_Root_Volume(cm3)",
                     'Convex_Hull_Area(cm2)', 'Max_Root_Depth(cm)'])
        self.file_array = file_array
        temp_list = []
        # 原图
        for name in img_list:
            if (name.split("_")[-1] == "W.jpg"):
                temp_list.append(name)
        for img in temp_list:
            self.img_analysis_b_m(img)
        self.df.to_csv(self.conf["out_path"] + "/" + "result.csv", index=False)

    def check_pxiel(self, src):
        check_res = np.where(src > 10)
        if int(check_res[0].shape[0]) == 0:
            return 0
        else:
            return 1

    def img_analysis_b_m(self, img):
        src = cv.imread(self.conf["predict_out_path"] + img)
        r, new = cv.threshold(src, 127, 255, cv.THRESH_BINARY)
        gray_img = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
        try:
            check_res = self.check_pxiel(gray_img)
            if check_res == 0:
                raise ValueError("None root pixels")
        except ValueError as e:
            # If the root system is not segmented, this message is returned and all processes are terminated
            msg = "We did not detect any root pixels. Please check the uploaded images and resubmit the task."
            send_mail_user(msg, self.conf)
            update_task_error(self.tid)
            exit()
        else:
            # Analysis of the connectivity domain
            parr, imgxx = self.draw_connect(src, 0)
            # Image Skeleton Extraction
            thinimg = self.img_thin(new)
            # root length (primary root + branched root)
            all_length, all_pnum_l = self.count_length(thinimg)
            # root projected area (primary root + branched root)
            all_area, all_pnum_a = self.count_area(parr)
            r, new2 = cv.threshold(gray_img, 100, 255, cv.THRESH_BINARY)
            # root surface area (primary root + branched root)
            all_surface_area = self.count_surface_area(new2)
            convex_area = self.count_convex_hull_area(gray_img)
            max_root_depth = self.count_depth(new2)
            volume = self.count_volume(all_surface_area, all_length)

            imgname = img.split("_out_B_M_W.jpg")[0] + "_out_MW.jpg"
            m_src = cv.imread(self.conf["predict_out_path"] + imgname)
            r1, t1 = cv.threshold(m_src, 127, 255, cv.THRESH_BINARY)
            # Analysis of the connectivity domain
            m_parr, m_imgxx = self.draw_connect(t1, 0)
            # Image Skeleton Extraction
            m_thinimg = self.img_thin(t1)
            # root length (primary root)
            m_length, m_pnum_l = self.count_length(m_thinimg)
            # root projected area (primary root)
            m_area, m_pnum_a = self.count_area(t1)
            # root surface area (primary root)
            m_surface_area = self.count_surface_area(t1)
            m_volume = self.count_volume(m_surface_area, m_length)
            data = {
                "Image_Name": self.file_array[img.split("_out_B_M_W.jpg")[0]],
                "Total_Root_Length(cm)": round(all_length, 3),
                "Total_Root_Projected_Area(cm2)": round(all_area, 3),
                'Total_Surface_Area(cm2)': round(all_surface_area, 3),
                'Total_Root_Volume(cm3)': round(volume, 3),
                "Primary_Root_Length(cm)": round(m_length, 3),
                "Primary_Root_Projected_Area(cm2)": round(m_area, 3),
                'Primary_Root_Surface_Area(cm2)': round(m_surface_area, 3),
                'Primary_Root_Volume(cm3)': round(m_volume, 3),
                'Convex_Hull_Area(cm2)': round(convex_area, 3),
                'Max_Root_Depth(cm)': round(max_root_depth, 3)
            }
            self.df = self.df.append(data, ignore_index=True)

    def draw_connect(self, image, type):
        if type == 1:
            gray = image.copy()
        else:
            gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
        ret, binary = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
        imgxx = image.copy()
        lable = measure.label(binary, connectivity=2)
        props = measure.regionprops(lable, intensity_image=None, cache=True)
        parr = []
        for i in range(len(props)):
            parr.append([i, props[i].coords])
        return parr, imgxx

    def img_thin(self, img):
        skeleton = skeletonize(img)
        gray = cv.cvtColor(skeleton, cv.COLOR_RGB2GRAY)
        gray = np.where(gray > 1, 255, 0)
        return gray

    def count_length(self, thinimg):
        pixelnum = (thinimg[:, :] == 255).sum()
        length = pixelnum * self.conf["length_ratio"]
        return length, pixelnum

    def count_area(self, parr):
        pixelnum = 0
        for p in range(0, len(parr)):
            pixelnum = pixelnum + len(parr[p][1])
        area = pixelnum * self.conf["area_ratio"]
        return area, pixelnum

    def count_depth(self, img):
        first = np.where(img == 255)[0][0] * self.conf["length_ratio"]
        last = np.where(img == 255)[0][-1] * self.conf["length_ratio"]
        depth = last - first
        return depth

    def count_volume(self, surface_area, all_length):
        volume = math.pi * surface_area * surface_area / 4 / all_length * 0.1
        return volume

    def count_surface_area(self, img):
        can = cv.Canny(img, 1, 255)
        area = np.where(img == 255)[0].shape[0]
        edge = np.where(can == 255)[0].shape[0]
        surface_area = (area - (edge / 2 + 1)) * 3.1415926535 * self.conf["area_ratio"]
        return surface_area

    def count_convex_hull_area(self, img):
        points = convex_hull_image(img)
        convexhull_area = np.where(points == True)[0].shape[0] * self.conf["area_ratio"]
        return convexhull_area
