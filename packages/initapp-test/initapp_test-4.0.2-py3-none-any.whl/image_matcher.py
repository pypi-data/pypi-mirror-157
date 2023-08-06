import math
import os

import cv2
import numpy as np
from match_conf import get_config_value

import constants
import matching
import tmp_image_utils
import time
import shutil
import pytesseract
import match_conf
from util.logger import logger


class image_matcher:
    vedio_load_tmp_path = ''
    vedio_load_tmp_dir = ''

    feed_appear = False
    video_loading_apper = False
    has_video_loading = True
    tab_contents = ''
    ad_text = ''
    is_ad_video = False

    def __init__(self):
        self.pkg_name = get_config_value('pkg_name')
        self.tab_contents = match_conf.get_feed_tab_text(self.pkg_name)
        self.ad_text = match_conf.get_ad_text(self.pkg_name)
        self.is_ad_video = False

    def set_vedio_load_tmp_dir(self, vedio_load_tmp_dir):
        self.vedio_load_tmp_dir = vedio_load_tmp_dir

    # 有多个模版tmp
    def corn_match_tmps(self, tmp_path, imagepath, match_ratio, match_count):
        if tmp_path == '' and tmp_image_utils.isEmpty(self.vedio_load_tmp_path):
            return False
        if tmp_image_utils.isEmpty(self.vedio_load_tmp_path) and os.path.isdir(tmp_path):
            match = False
            for f in self.list_filter(os.listdir(tmp_path)):
                tmp_p = os.path.join(tmp_path, f)
                if os.path.isfile(tmp_p):
                    match = self.corn_match(tmp_p, imagepath, match_ratio, match_count)
                if match:
                    #self.vedio_load_tmp_path = tmp_p
                    return True
        elif not tmp_image_utils.isEmpty(self.vedio_load_tmp_path):
            return self.corn_match(self.vedio_load_tmp_path, imagepath, match_ratio, match_count)
        else:
            self.vedio_load_tmp_path = tmp_path
            return self.corn_match(tmp_path, imagepath, match_ratio, match_count)


    # 有多个模版tmp
    def match_tmps(self, tmp_path, imagepath, match_ratio, match_count):
        if tmp_path == '' and tmp_image_utils.isEmpty(self.vedio_load_tmp_path):
            return False
        img = cv2.imread(imagepath, 0)
        if tmp_image_utils.isEmpty(self.vedio_load_tmp_path) and os.path.isdir(tmp_path):
            match = False
            for f in self.list_filter(os.listdir(tmp_path)):
                tmp_p = os.path.join(tmp_path, f)
                if os.path.isfile(tmp_p):
                    img_tmp = cv2.imread(tmp_p, 0)
                    match = matching.match2(img_tmp, img, match_ratio, match_count)
                if match:
                    #self.vedio_load_tmp_path = tmp_p
                    return True
        elif not tmp_image_utils.isEmpty(self.vedio_load_tmp_path):
            img_tmp = cv2.imread(self.vedio_load_tmp_path, 0)
            return matching.match2(img_tmp, img, match_ratio, match_count)
        else:
            self.vedio_load_tmp_path = tmp_path
            img_tmp = cv2.imread(self.vedio_load_tmp_path, 0)
            return matching.match2(img_tmp, img, match_ratio, match_count)

    def match_tmps1(self, tmp_path, img, match_ratio, match_count):
        if tmp_path == '' and tmp_image_utils.isEmpty(self.vedio_load_tmp_path):
            return False
        if tmp_image_utils.isEmpty(self.vedio_load_tmp_path) and os.path.isdir(tmp_path):
            match = False
            for f in self.list_filter(os.listdir(tmp_path)):
                tmp_p = os.path.join(tmp_path, f)
                if os.path.isfile(tmp_p):
                    img_tmp = cv2.imread(tmp_p, 0)
                    match = matching.match2(img_tmp, img, match_ratio, match_count)
                    if match:
                        #self.vedio_load_tmp_path = tmp_p
                        return True
                    else:
                        for i in range(220, 254, 5):
                            ret, img1 = cv2.threshold(img, i, 255, cv2.THRESH_BINARY)
                            ret, img_tmp1 = cv2.threshold(img_tmp, i, 255, cv2.THRESH_BINARY)
                            match = matching.match1(img_tmp, img1, 'sift', match_ratio, 0.1, 4)
                            if match:
                                return True

        elif not tmp_image_utils.isEmpty(self.vedio_load_tmp_path):
            img_tmp = cv2.imread(self.vedio_load_tmp_path, 0)
            return matching.match2(img_tmp, img, match_ratio, match_count)
        else:
            self.vedio_load_tmp_path = tmp_path
            img_tmp = cv2.imread(self.vedio_load_tmp_path, 0)
            return matching.match2(img_tmp, img, match_ratio, match_count)


    def corn_match(self, tmppath, imagepath, match_ratio, match_count):
        if tmppath == '':
            return False

        tmp_img = cv2.imread(tmppath, 0)  # 原图为彩色图，可将第二个参数变为0，为灰度图
        img = cv2.imread(imagepath, 0)

        h_t, w_t = tmp_img.shape[:2]
        h_img, w_img = img.shape[:2]

        mask_tmp = np.zeros_like(tmp_img)
        roi_tmp = self.__get_process_roi(h_t, w_t)

        mask_tmp[roi_tmp[0]:roi_tmp[1], roi_tmp[2]:roi_tmp[3]] = 255  # y0:y1, x0:x1

        roi_img = self.__get_process_roi(h_img, w_img)
        mask_img = np.zeros_like(img)
        mask_img[roi_img[0]:roi_img[1], roi_img[2]:roi_img[3]] = 255  # y0:y1, x0:x1
        tmp_corners = cv2.goodFeaturesToTrack(tmp_img, 500, 0.01, 0.1, mask=mask_tmp)  # 返回的结果是 [[ a., b.]] 两层括号的数组。

        img_corners = cv2.goodFeaturesToTrack(img, 500, 0.01, 0.1, mask=mask_img)  # 返回的结果是 [[ a., b.]] 两层括号的数组。
        if img_corners is None or len(img_corners) < 100:
            return False

        if tmp_corners is None or len(tmp_corners) == 0:
            self.has_video_loading = False
            return False

        tmp_corners = np.int0(tmp_corners)
        img_corners = np.int0(img_corners)

        # index = min(len(tmp_corners), len(img_corners))
        # for i in range(index):
        #     #print("tmp:", tmp_corners[i].ravel())
        #     #print("img:", img_corners[i].ravel())
        #     cv2.circle(tmp_img, tmp_corners[i].ravel(), 3, (255, 255, 0))
        #     cv2.circle(img, tmp_corners[i].ravel(), 3, (255, 255, 0))

        # 将角点画在图片上
        radius_rate = min(float(h_img / h_t), float(w_img / w_t))
        # cv2.circle(tmp_img, i.ravel(), int(3 * radius_rate), (255, 255, 0))
        for i in tmp_corners:
            cv2.circle(tmp_img, i.ravel(), 5, (255, 255, 0), thickness=-1)
        for i in img_corners:
            cv2.circle(img, i.ravel(), math.ceil(5), (255, 255, 0), thickness=-1)

        tmp_img = self.__process_tmp(tmp_img)
        img = self.__process_tmp(img)

        match = matching.match2(tmp_img, img, match_ratio, match_count)

        #math123 = compare_img.cmppHash1(tmp_img, img, True)

        return match
        # #
        cv2.imshow('frame', img)
        cv2.imshow('frame1', tmp_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def __process_tmp(self, image):
        h, w = image.shape[:2]
        roi = self.__get_process_roi(h, w)
        tmp = image[roi[0]:roi[1], roi[2]:roi[3]].copy()
        image[0:h, 0:w] = 255
        image[roi[0]:roi[1], roi[2]:roi[3]] = tmp
        return tmp


    # 三大 tab 出现的时间点
    def get_tab_match(self, image_path, tab_tmp_path, splash_tmp_path):

        if tab_tmp_path == '':
            return False
        tab_match = False
        image = cv2.imread(image_path, 0)

        if splash_tmp_path == '':
            return False
        splash_tmp_match = False
        if os.path.isdir(splash_tmp_path):
            for f in self.list_filter(os.listdir(splash_tmp_path)):
                tmp_p = os.path.join(splash_tmp_path, f)
                if os.path.isfile(tmp_p):
                    tab_tmp = cv2.imread(tmp_p, 0)
                    splash_tmp_match = matching.match2(tab_tmp, image, 0.4, 10)
                if not splash_tmp_match:
                    break

        else:
            tab_tmp = cv2.imread(splash_tmp_path, 0)
            splash_tmp_match = matching.match2(tab_tmp, image, 0.4, 10)

        if splash_tmp_match:
            return False

        if os.path.isdir(tab_tmp_path):
            for f in self.list_filter(os.listdir(tab_tmp_path)):
                tmp_p = os.path.join(tab_tmp_path, f)
                if os.path.isfile(tmp_p):
                    tab_tmp = cv2.imread(tmp_p, 0)
                    tab_match = matching.match2(tab_tmp, image, 0.4, 15)
                if tab_match:
                    break

        else:
            tab_tmp = cv2.imread(tab_tmp_path, 0)
            tab_match = matching.match2(tab_tmp, image, 0.4, 15)

        if not tab_match:
            tab_img = cv2.imread(image_path)
            logger.info(u'orc 图片地址:%s', image_path)
            tab_match = self.__ocr_tab_match(tab_img)
            if not tab_match:
                return False

        return tab_match and not splash_tmp_match

    # 获取feed数据返回加载时间点
    def get_feedback_match(self, imagepath):
        if self.pkg_name == constants.KWAI_PACKAGENAME:
            #self.feed_appear = self.corn_match_tmps(self.vedio_load_tmp_dir, imagepath, 0.5, 10)
            self.feed_appear = self.__get_kwai_feedback_appear(imagepath)
            self.video_loading_apper = self.feed_appear
            return self.feed_appear
        if self.pkg_name == constants.SNACK_PACKAGENAME:
            self.feed_appear = self.__get_kwai_feedback_appear(imagepath)
            #self.feed_appear = self.corn_match_tmps(self.vedio_load_tmp_dir, imagepath, 0.6, 10)
            return self.feed_appear
        elif self.pkg_name == constants.TT_PACKAGENAME:
            self.feed_appear = self.__get_TT_feedback_appear(imagepath)
            return self.feed_appear

    # 视屏开始播放
    def get_vedio_start_match(self, imagepath):
        # 对于 kwai， feed_appear=true && 没有匹配到 vedio_load_tmp 视为视屏开始播放
        if self.pkg_name == constants.KWAI_PACKAGENAME:
            if (self.__vedio_left_start(imagepath) or not self.corn_match_tmps(self.vedio_load_tmp_dir, imagepath, 0.5, 15)):
                self.video_loading_apper = False
                img = cv2.imread(imagepath, 0)
                h, w = img.shape[:2]
                roi = self.__get_process_roi(h, w)
                img = img[roi[0]:roi[1], roi[2]:roi[3]]
                return not matching.roi_not_change(img,15 ,5)
            # if not self.video_loading_apper:
            #     img = cv2.imread(imagepath, 0)
            #     h, w = img.shape[:2]
            #     roi = self.__get_process_roi(h, w)
            #     img = img[roi[0]:roi[1], roi[2]:roi[3]]
            #     return not matching.roi_not_change(img,15 ,5)
            return False
            #return not self.corn_match_tmps(self.vedio_load_tmp_dir, imagepath, 0.5, 10)

        if self.pkg_name == constants.SNACK_PACKAGENAME:
            if (self.__vedio_left_start(imagepath) or not self.corn_match_tmps(self.vedio_load_tmp_dir, imagepath, 0.5, 15)):
                img = cv2.imread(imagepath, 0)
                h, w = img.shape[:2]
                roi = self.__get_process_roi(h, w)
                img = img[roi[0]:roi[1], roi[2]:roi[3]]
                return not matching.roi_not_change(img,15 ,5)
            return False
        # 对于TT， feed_appear=true && 特定区域内 图片 有变化，视为视屏开始播放
        if self.pkg_name == constants.TT_PACKAGENAME:
            img = cv2.imread(imagepath, 0)
            h,w = img.shape[:2]
            roi = self.__get_process_roi(h, w)
            img = img[roi[0]:roi[1],roi[2]:roi[3]]
            return self.feed_appear and not matching.roi_not_change(img,15 ,5)
            #return matching.roi_not_change(img,15 ,5)



    # 获取TT feed 数据返回时间点（点赞，评论区域不为纯色区域时，视为出现），todo 该方法判断点赞，评论区域出现不准确判断方法待改进
    def __get_TT_feedback_appear(self, imagepath):
        img = cv2.imread(imagepath, 0)
        h,w = img.shape[:2]
        roi = self.__get_like_comment_share_roi(h, w)
        img_feed = img[roi[0]:roi[1] , roi[2]:roi[3]]
        like_comment_dir = tmp_image_utils.get_like_comment_tmp_img_dir(self.pkg_name, (w,h))
        feed_appear = not matching.roi_not_change(img_feed, 50, 20) and self.match_tmps1(like_comment_dir, img_feed, 0.4, 5)
        if not feed_appear:
            ret, img_feed = cv2.threshold(img_feed, 210, 255, cv2.THRESH_BINARY)
            feed_appear = not matching.roi_not_change(img_feed, 50, 20) and self.match_tmps1(like_comment_dir, img_feed, 0.4, 5)
        return feed_appear


    # 获取TT feed 数据返回时间点（点赞，评论区域不为纯色区域时，视为出现），todo 该方法判断点赞，评论区域出现不准确判断方法待改进
    # kwai 中的视屏加载占位图回和点赞评论一起出现，将出现的占位图比较后保存为模版
    def __get_kwai_feedback_appear(self, imagepath):
        img = cv2.imread(imagepath, 0)
        self.__ocr_is_ad(img)
        if self.is_ad_video:
            return False
        h,w = img.shape[:2]
        roi = self.__get_like_comment_share_roi(h, w)
        img_feed = img[roi[0]:roi[1] , roi[2]:roi[3]]
        like_comment_dir = tmp_image_utils.get_like_comment_tmp_img_dir(self.pkg_name, (w,h))
        feed_appear = not matching.roi_not_change(img_feed, 50, 20) and self.match_tmps1(like_comment_dir, img_feed, 0.5, 5)
        if not feed_appear:
            ret, img_feed = cv2.threshold(img_feed, 245, 255, cv2.THRESH_BINARY)
            feed_appear = not matching.roi_not_change(img_feed, 50, 20) and self.match_tmps1(like_comment_dir, img_feed,
                                                                                             0.5, 5)
        scaled_vedio_load_tmp_dir = tmp_image_utils.get_scaled_vedio_tmp_img_dir(self.pkg_name, (w, h))
        if not self.feed_appear and feed_appear:
            auto_tmp_path = 'vedio_load_tmp_auto_{}.jpg'.format(int(time.time()))
            if not os.path.exists(scaled_vedio_load_tmp_dir):
                os.mkdir(scaled_vedio_load_tmp_dir)
                cv2.imwrite(os.path.join(scaled_vedio_load_tmp_dir, auto_tmp_path),img)
                if not self.vedio_load_tmp_dir == scaled_vedio_load_tmp_dir:
                    for f in self.list_filter(os.listdir(self.vedio_load_tmp_dir)):
                        tmp_p = os.path.join(self.vedio_load_tmp_dir, f)
                        if os.path.isfile(tmp_p):
                            shutil.copy(tmp_p, os.path.join(scaled_vedio_load_tmp_dir, f))
            else:
                if not self.corn_match_tmps(scaled_vedio_load_tmp_dir, imagepath, 0.4, 20) and self.has_video_loading:
                    cv2.imwrite(os.path.join(scaled_vedio_load_tmp_dir, auto_tmp_path), img)

            self.vedio_load_tmp_dir = scaled_vedio_load_tmp_dir
        self.feed_appear = feed_appear
        logger.info(u'feed appear:%s  path:%s', str(self.feed_appear), imagepath)
        return self.feed_appear



    # 视屏左边是否开始播放
    def __vedio_left_start(self, imagepath):
        img = cv2.imread(imagepath, 0)
        h, w = img.shape[:2]
        roi = self.__get_vedio_left_roi(h, w)
        img = img[roi[0]:roi[1], roi[2]:roi[3]]
        return not matching.roi_not_change(img, 15, 5)

    def __get_process_roi(self, h, w):
        if self.pkg_name == constants.KWAI_PACKAGENAME:
            if str(w) + '_' + str(h) == '600_1280':
                return (int(h / 3), int(h / 9 * 5), int(w / 3), int(w / 3 * 2))
            elif str(w) + '_' + str(h) == '592_1280':
                # return (int(h / 3), int(h / 12 * 6), int(w/3), int(w/3 * 2))
                return (int(h / 3), int(h / 9 * 5), int(w / 3), int(w / 3 * 2))
            elif str(w) + '_' + str(h) == '720_1280':
                return (int(h / 3), int(h / 9 * 6), int(w / 3), int(w / 3 * 2))
            else:
                return (int(h / 3), int(h / 9 * 5), int(w / 3), int(w / 3 * 2))
        elif self.pkg_name == constants.SNACK_PACKAGENAME:
            if str(w) + '_' + str(h) == '720_1280':
                return (int(h / 3), int(h / 3 * 2), int(w / 3), int(w / 3 * 2))
            elif str(w) + '_' + str(h) == '592_1280':
                # return (int(h / 3), int(h / 12 * 6), int(w/3), int(w/3 * 2))
                return (int(h / 3), int(h / 9 * 5), int(w / 3), int(w / 3 * 2))
            else:
                return (int(h / 3), int(h / 3 * 2), int(w / 3), int(w / 3 * 2))
        elif self.pkg_name == constants.TT_PACKAGENAME:
            if str(w) + '_' + str(h) == '600_1280':
                return (int(h / 6), int(h / 9 * 5), int(w / 5), int(w / 5 * 4))
            elif str(w) + '_' + str(h) == '720_1280':
                return (int(h / 6), int(h / 9 * 5), int(w / 5), int(w / 5 * 4))
            else:
                return (int(h / 6), int(h / 9 * 5), int(w / 5), int(w / 5 * 4))

    def __get_vedio_left_roi(self, h, w):
        if self.pkg_name == constants.TT_PACKAGENAME:
            return (int(h / 6), int(h / 9 * 5), 0, int(w / 5 ))
        elif self.pkg_name == constants.SNACK_PACKAGENAME:
            return (int(h / 3), int(h / 9 * 5), 0, int(w / 3))
        elif self.pkg_name == constants.KWAI_PACKAGENAME:
            return (int(h / 3), int(h / 9 * 5), 0, int(w / 3))


    # 获取右边 点赞，评论，区域的roi
    def __get_like_comment_share_roi(self, h, w):
        if self.pkg_name == constants.TT_PACKAGENAME:
            return (int(h/2), int(h/4*3), int(w / 5 * 4), int(w))
        elif self.pkg_name == constants.KWAI_PACKAGENAME or get_config_value('pkg_name') == constants.SNACK_PACKAGENAME:
            return (int(h/9 * 4), int(h/5*4), int(w / 8 * 7), int(w))
        else:
            return (int(h / 2), int(h / 4 * 3), int(w / 5 * 4), int(w))

    def __file_filter(self, f):
        if f[-4:] in ['.jpg', '.png', '.bmp']:
            return True
        else:
            return False

    def list_filter(self, files):
        return list(filter(self.__file_filter, files))

    # 获取tab 区域
    def __get_tab_roi(self, h, w):
        if self.pkg_name == constants.TT_PACKAGENAME:
            if str(w) + '_' + str(h) == '750_1334':
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))
            else:
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))

        elif self.pkg_name == constants.KWAI_PACKAGENAME:
            if str(w) + '_' + str(h) == '750_1334':
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))
            elif str(w) + '_' + str(h) == '720_1560':
                return (int(h / 50 * 2), int(h / 50 * 5), 0, int(w))
            else:
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))

        elif self.pkg_name == constants.SNACK_PACKAGENAME:
            if str(w) + '_' + str(h) == '750_1334':
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))
            elif str(w) + '_' + str(h) == '1440_3040':
                return (int(h / 40 * 2), int(h / 40 * 4), 0, int(w))
            else:
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))

    # 获取ad_text 区域
    def __get_ad_roi(self, h, w):
        if self.pkg_name == constants.TT_PACKAGENAME:
            if str(w) + '_' + str(h) == '750_1334':
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))
            else:
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))

        elif self.pkg_name == constants.KWAI_PACKAGENAME:
            if str(w) + '_' + str(h) == '750_1334':
                return (int(h / 40 * 1), int(h / 40 * 3), 0, int(w))
            elif str(w) + '_' + str(h) == '720_1560':
                return (int(h / 50 * 2), int(h / 50 * 5), 0, int(w))
            else:
                return (int(h / 40 * 1), int(h / 40 * 3), 0, int(w))

        elif self.pkg_name == constants.SNACK_PACKAGENAME:
            if str(w) + '_' + str(h) == '750_1334':
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))
            elif str(w) + '_' + str(h) == '1440_3040':
                return (int(h / 40 * 2), int(h / 40 * 4), 0, int(w))
            else:
                return (int(h / 40 * 2), int(h / 40 * 3), 0, int(w))

    # ocr 识别3大tab
    def __ocr_tab_match(self, img):
        if not self.tab_contents:
            return False
        logger.info(u'orc 模版内容:%s', str(self.tab_contents))
        h, w = img.shape[:2]
        roi = self.__get_tab_roi(h, w)
        tab = img[roi[0]:roi[1], roi[2]:roi[3]]

        config = ("--psm 6")
        # cv2.imshow('frame', tab)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        tab_content = pytesseract.image_to_string(tab, config=config)
        logger.info(u'orc 内容:%s', str(tab_content))
        if self.__is_ad(tab_content):
            self.is_ad_video = True
            logger.info(u'ad video')
            return False
        for content in self.tab_contents:
            content = content.strip()
            if not tmp_image_utils.isEmpty(content) and content in tab_content:
                return True

        # 如果没有识别，尝试灰度，二值化后再次识别
        cv2.cvtColor(tab, cv2.COLOR_BGR2GRAY)
        for i in range(220, 254, 5):
            ret, tab1 = cv2.threshold(tab, i, 255, cv2.THRESH_BINARY)
            tab_content = pytesseract.image_to_string(tab1, config=config)
            logger.info(u'orc 内容:%s', str(tab_content))
            if self.__is_ad(tab_content):
                self.is_ad_video = True
                logger.info(u'ad video')
                return False
            for content in self.tab_contents:
                content = content.strip()
                if not tmp_image_utils.isEmpty(content) and content in tab_content:
                    return True
        return False

    def __ocr_match(self, img, tmp_contents):
        if not tmp_contents:
            return False
        logger.info(u'orc 模版内容:%s', str(tmp_contents))

        config = ("--psm 6")
        tab_content = pytesseract.image_to_string(img, config=config)
        logger.info(u'orc 内容:%s', str(tab_content))
        for content in tmp_contents:
            content = content.strip()
            if not tmp_image_utils.isEmpty(content) and content in tab_content:
                logger.info(u'找到模版文字内容:%s', str(content))
                return True

        # # 如果没有识别，尝试灰度，二值化后再次识别
        # cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        for i in range(220, 254, 5):
            ret, tab1 = cv2.threshold(img, i, 255, cv2.THRESH_BINARY)
            tab_content = pytesseract.image_to_string(tab1, config=config)
            logger.info(u'orc 内容:%s', str(tab_content))
            for content in tmp_contents:
                content = content.strip()
                if not tmp_image_utils.isEmpty(content) and content in tab_content:
                    logger.info(u'找到模版文字内容:%s', str(content))
                    return True
        return False

    def __ocr_is_ad(self, img):
        h, w = img.shape[:2]
        roi = self.__get_ad_roi(h, w)
        tab = img[roi[0]:roi[1], roi[2]:roi[3]]
        if self.__ocr_match(tab, self.ad_text):
            self.is_ad_video = True
            logger.info(u'ad video')
            return True
        return False

    def __is_ad(self, tab_content):
        for content in self.ad_text:
            content = content.strip()
            if not tmp_image_utils.isEmpty(content) and content in tab_content:
                return True
        return False

    # def is_ad_video(self):
    #     return self.is_ad_video

    def clear_tmp_auto_create_img(self, h, w):
        vediotmpdir = tmp_image_utils.get_scaled_vedio_tmp_img_dir(self.pkg_name, (w, h))
        if not os.path.exists(vediotmpdir):
            return
        for f in os.listdir(vediotmpdir):
            if "vedio_load_tmp_auto" in f:
                tmp_p = os.path.join(vediotmpdir, f)
                os.remove(tmp_p)

    def is_black(self, img_path):
        img = cv2.imread(img_path, 0)
        h, w = img.shape[:2]
        roi = self.__get_process_roi(h, w)
        img = img[roi[0]:roi[1], roi[2]:roi[3]]
        return matching.roi_not_change(img, 5, 2) and np.max(img) < 2

if __name__ == '__main__':


    matcher = image_matcher()
    img = cv2.imread('imagedir/92.jpg', 0)

    matcher.ocr_tab_match(img)
    #h, w = img.shape[:2]
    # roi = matcher.get_tab_roi(h, w)
    # tab = img[roi[0]:roi[1], roi[2]:roi[3]]
    # cv2.imwrite('test.jpg', tab)
