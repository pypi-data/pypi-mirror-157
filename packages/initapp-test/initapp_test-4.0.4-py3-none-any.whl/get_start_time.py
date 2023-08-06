import read_frame as gread_frame
import matching as match
import numpy
import cv2
import os
import shutil
import compare_img as cmp
from util.logger import logger
from match_conf import get_config_value
import tmp_image_utils
import image_matcher
import util.result_util as result_util
import glob
import datetime
import constants


class StartTime:

    video_info = None
    vedio_load_tmp_path = ''
    only_app_start = False

    # 分割视屏保存图片的目录
    image_dir = "imagedir"
    save_image_dir = 'saveimage'
    save_image_day = 2
    #vediopath = "brvideo/TT-IOS/TT9.mp4"
    vediopath = "/Users/wangkejun/Library/Application Support/Kim (Kim)/userData/n9gqSZvyf7iGTH72A/Kim file/2021-10/kwai1029-A11/kwai8.mp4"
    #vediopath = "provideo1/kwai0.mp4"
    scale_vedio_path = 'scaled_video.mp4'

    def __init__(self, start_step : int = 0):
        self.pkg_name = get_config_value('pkg_name')
        self.start_step = start_step

    def getStartTime(self):
        logger.info(u'开始获取耗时:%s  instance:%s  pkg:%s', str(self.vediopath), self, self.pkg_name)
        img_matcher = image_matcher.image_matcher()
        start_step = self.start_step
        # app启动开始的图片
        start_time_index = 0
        start_complete_index = 0
        start_time_cost = 0
        vedio_start_load_index = 0
        vedio_load_complete_index = 0
        vedio_load_cost_time = 0
        total_cost_time = 0
        time_cost_dict = {}

        logger.info("imgdir 文件数1：%s", len(glob.glob('imagedir/*')))
        self.__clear_word_data(self.image_dir, self.scale_vedio_path)
        logger.info("imgdir 文件数2：%s", len(glob.glob('imagedir/*')))
        # 修改视屏
        gread_frame.scale_video(self.vediopath, self.scale_vedio_path)

        get_start_time = False
        find_vedio_loading = False

        if os.path.isfile(self.scale_vedio_path):
            self.video_info = gread_frame.get_video_info(self.scale_vedio_path)
        else:
            self.video_info = gread_frame.get_video_info(self.vediopath)

        total_duration = self.video_info['duration']
        float_time = float(total_duration)
        #time_interval = float(total_duration)/10
        # 分帧精度
        time_interval = 0.05
        logger.info('总时间：' + str(total_duration) + 's')
        #cut_couts = int(float_time * 10)
        cut_couts = int(float_time / time_interval)
        time_offset = 0

        # 获取视频加载模版图片path
        test_type = get_config_value('test_type')
        width = self.video_info['width']
        height = self.video_info['height']
        logger.info(u"视屏scale: %s  ", str(width) + str(height))
        self.vedio_load_tmp_path = tmp_image_utils.get_vedio_tmp_img_dir(self.pkg_name, (width, height))
        img_matcher.set_vedio_load_tmp_dir(self.vedio_load_tmp_path)
        img_matcher.clear_tmp_auto_create_img(height, width)


        #各关键点出现标志
        # 3大tab是否已经出现
        start_tab_end = False
        time_offset = start_step * time_interval

        logger.info(u'图片总数:%s ', str(cut_couts - 1))

        for index in range(start_step, cut_couts - 1):
            time_offset += time_interval
            time_offset = min(time_offset, float(total_duration) - 0.1)
        # random_time = random.randint(1, int(float(total_duration)) - 1) + random.random()
        # print('随机时间：' + str(random_time) + 's')
        #     out = gread_frame.read_frame_by_time(self.vediopath, time_offset)
        #     if out == b'':
        #         break
        #     image_array = numpy.asarray(bytearray(out), dtype="uint8")
        #     image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        # #cv2.imshow('frame', image)
        # #cv2.waitKey()
        #     image_path = self.image_dir + os.sep + str(index) + ".jpg"
        #     cv2.imwrite(image_path, image)
            image_path = self.image_dir + os.sep + str(index) + ".jpg"
            if os.path.isfile(self.scale_vedio_path):
                out, err = gread_frame.read_frame_by_time1(self.scale_vedio_path, time_offset, image_path)
            else:
                out, err = gread_frame.read_frame_by_time1(self.vediopath, time_offset, image_path)

            if not os.path.isfile(image_path):
                break
            # 获取app启动开始的时间
            if index > start_step:
                imagepath1 = self.image_dir + os.sep + str(start_step) + ".jpg"
                if start_time_index == 0 and (not cmp.cmppHash(imagepath1, image_path)):
                    start_time_index = index - 1
                    logger.info(u'app启动开始index:%s', str(start_time_index))
                if start_time_index == 0:
                    continue

            if img_matcher.is_ad_video:
                break

            if not get_start_time and img_matcher.get_tab_match(image_path, tmp_image_utils.get_tab_tmp_dir(self.pkg_name, (width, height)), tmp_image_utils.get_splash_tmp_dir(self.pkg_name, (width, height))):
                get_start_time = True
                start_tab_end = True
                time_cost = (index - start_time_index) * time_interval
                start_complete_index = index
                start_time_cost = time_cost
                total_cost_time = time_cost
                logger.info(u'app启动完成index:%s', str(index))
                logger.info(u"启动耗时：%s" , str(time_cost))
                if self.only_app_start:
                    break

            # if find_vedio_loading and not match.match_vedio_load('5.png', image_path):
            #     time_cost = (index - start_time_index) * time_interval
            #     print(u'app开始播放视频index:', index)
            #     print(u"app开始播放视频耗时：" + str(time_cost))
            #     break
            if get_start_time:
                if vedio_load_complete_index ==0 and img_matcher.get_vedio_start_match(image_path):
                    vedio_load_complete_index = index
                    time_cost = (vedio_load_complete_index - start_complete_index) * time_interval
                    vedio_load_cost_time = time_cost
                    logger.info(u'app开始播放视频index:%s', str(index))
                    logger.info(u"app开始播放视频耗时：%s" , str(time_cost))


                #if not tmp_image_utils.isEmpty(self.vedio_load_tmp_path) and not find_vedio_loading and self.__vedio_start(image_path):
                if not find_vedio_loading and img_matcher.get_feedback_match(image_path):
                    logger.info(u'loading index:%s', str(index))
                    vedio_start_load_index = index
                    find_vedio_loading = True

            if vedio_load_complete_index != 0 and vedio_start_load_index !=0:
                total_cost_time = index * time_interval
                break
        if not get_start_time:
            logger.info(u"视屏时间内未发现启动")

        if img_matcher.is_ad_video:
            logger.info(u"视频为广告")
            time_cost_dict[constants.RESULT_IS_AD] = True

        logger.info(u"app启动开始index: %s  time: %s",str(start_time_index), str(start_time_index * time_interval))
        time_cost_dict[constants.RESULT_APP_START_TIME] = start_time_index * time_interval
        logger.info(u"app启动完成index: %s  time: %s",str(start_complete_index), str(start_complete_index * time_interval))
        time_cost_dict[constants.RESULT_APP_TAB_APPEAR_TIME] = start_complete_index * time_interval
        logger.info(u"app启动完成耗时:%s",str(start_time_cost))
        logger.info(u"视频load开始index:%s  time: %s",str(vedio_start_load_index),str(vedio_start_load_index * time_interval))
        time_cost_dict[constants.RESULT_APP_FEED_APPEAR_TIME] = vedio_start_load_index * time_interval
        logger.info(u"视频load完成index:%s  time: %s",str(vedio_load_complete_index), str(vedio_load_complete_index * time_interval))
        time_cost_dict[constants.RESULT_APP_VEDIO_START_TIME] = vedio_load_complete_index * time_interval
        logger.info(u"视频load耗时:%s",str(vedio_load_cost_time))
        logger.info(u"总耗时:%s",str(total_cost_time))

        if vedio_load_complete_index == 0 or start_complete_index == 0:
            logger.info(u"为识别视屏: %s  ", str(self.vediopath))
            time_cost_dict[constants.RESULT_NOT_RECOGNIZE_VEDIO] = True

        time_cost_dict[constants.RESULT_VEDIO_PATH] = self.vediopath
        time_cost_dict[constants.RESULT_APP_START_TIME_COST] = str(start_time_cost)
        #time_cost_dict['vedio_load_cost_time'] = str(vedio_load_cost_time)
        time_cost_dict[constants.RESULT_TOTAL_TIME_COST] = total_cost_time

        self.save_img_dir(self.image_dir)

        return time_cost_dict

    # 3大tab出现
    def __get_tab_match(self, image_path, tab_tmp_path, splash_tmp_path):
        image = cv2.imread(image_path, 0)
        tab_tmp = cv2.imread(tab_tmp_path, 0)
        splash_tmp = cv2.imread(splash_tmp_path, 0)
        if match.match2(tab_tmp, image, 0.4, 20) and not match.match2(splash_tmp, image, 0.5, 10):
            return True
        return False


    def __clear_word_data(self, image_dir, scale_vedio_path):
        if os.path.exists(image_dir):
            #os.removedirs(image_dir)
            shutil.rmtree(image_dir)
        os.mkdir(image_dir)

        if os.path.exists(scale_vedio_path):
            os.remove(scale_vedio_path)

        if os.path.exists(self.save_image_dir):
            for f in os.listdir(self.save_image_dir):
                if f not in self.__get_save_img_dir():
                    shutil.rmtree(os.path.join(self.save_image_dir, f))

    def __get_save_img_dir(self):
        save_img_list = []
        for i in range(self.save_image_day):
            now = datetime.datetime.now()
            delta = datetime.timedelta(days=-i)
            n_days = now + delta
            save_img_list.append(n_days.strftime('%Y%m%d'))
        return save_img_list





    # 保存图片文件
    def save_img_dir(self, image_dir):
        now = datetime.datetime.now()
        time = now.strftime('%Y%m%d')
        timestamp = int(now.timestamp())
        logger.info("vediopath:%s timestamp:%d", self.vediopath, timestamp)
        img_save_dir = self.save_image_dir + os.sep + time
        if not os.path.exists(img_save_dir):
            os.makedirs(img_save_dir)
        img_save_path = os.path.join(img_save_dir, str(timestamp))
        os.rename(image_dir, img_save_path)



if __name__ == '__main__':
    startTime = StartTime()
    startTime.getStartTime()

    #match.match_vedio_load(tmp_image_utils.get_vedio_tmp_img_dir('com.kwai.video', (368,800)), 'imagedir/281.jpg')
    #matcher = image_matcher.image_matcher()
    #matcher.get_feedback_match('imagedir/119.jpg')
    # matcher.get_vedio_start_match('imagedir/109.jpg')

    # matcher.set_vedio_load_tmp_dir('tmp_img/android/kwai/vediotmp/720_1560')
    #matcher.get_feedback_match('imagedir/110.jpg')
    # matcher.get_vedio_start_match('imagedir/220.jpg')
    #matcher.get_tab_match('imagedir/112.jpg', tmp_image_utils.get_tab_tmp_dir('com.kwai.video', (720, 1560)), tmp_image_utils.get_splash_tmp_dir('com.kwai.video'))
    #match.corn_match_tmps(tmp_image_utils.get_vedio_tmp_img_dir('com.kwai.video', (600,1280)), 'imagedir/130.jpg')

    #startTime.get_tab_match('imagedir/50.jpg', tmp_image_utils.get_tab_tmp('com.kwai.video'), tmp_image_utils.get_splash_tmp('com.kwai.video'))

