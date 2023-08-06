# 获取模版图片文件
import os
import constants
from match_conf import get_config_value

DIR = os.path.dirname(__file__)
def get_vedio_tmp_img(packagename, scale):
    type = get_config_value('test_type')
    if packagename == "com.kwai.video":
        if type == "android":
            path = 'tmp_img/android/kwai/' + str(scale[0]) + '_' + str(scale[1]) + '/vedio_load_tmp.jpg'
            path = os.path.join(DIR, path)
            path = 'tmp_img/android/kwai/vediotmp/vedio_load_tmp.jpg'
            path = os.path.join(DIR, path)
            if os.path.exists(path):
                return path
        elif type == "ios":
            path = 'tmp_img/ios/kwai/' + str(scale[0]) + '_' + str(scale[1]) + '/vedio_load_tmp.jpg'
            path = 'tmp_img/ios/kwai/vediotmp/vedio_load_tmp.jpg'
            path = os.path.join(DIR, path)
            if os.path.exists(path):
                return path

    return ''

def get_vedio_tmp_img_dir(packagename, scale):
    type = get_config_value('test_type')
    if packagename == constants.KWAI_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/kwai/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/android/kwai/vediotmp/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
        elif type == "ios":
            path = 'tmp_img/ios/kwai/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/ios/kwai/vediotmp/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
    elif packagename == constants.SNACK_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/snack/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/android/snack/vediotmp/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
        elif type == "ios":
            path = 'tmp_img/ios/snack/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/ios/snack/vediotmp/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default

    return ''


def get_like_comment_tmp_img_dir(packagename, scale):
    type = get_config_value('test_type')
    if packagename == constants.KWAI_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/kwai/feed/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/android/kwai/feed/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
        elif type == "ios":
            path = 'tmp_img/ios/kwai/feed/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/ios/kwai/feed/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
    elif packagename == constants.SNACK_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/snack/feed/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/android/snack/feed/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
        elif type == "ios":
            path = 'tmp_img/ios/snack/feed/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/ios/snack/feed/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
    elif packagename == constants.TT_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/TT/feed/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/android/TT/feed/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default
        elif type == "ios":
            path = 'tmp_img/ios/TT/feed/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            path_default = 'tmp_img/ios/TT/feed/'
            path_default = os.path.join(DIR, path_default)
            if os.path.exists(path):
                return path
            else:
                return path_default

    return ''


def get_scaled_vedio_tmp_img_dir(packagename, scale):
    type = get_config_value('test_type')
    if packagename == constants.KWAI_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/kwai/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            return path
        elif type == "ios":
            path = 'tmp_img/ios/kwai/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            return path
    elif packagename == constants.SNACK_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/snack/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            return path
        elif type == "ios":
            path = 'tmp_img/ios/snack/vediotmp/' + str(scale[0]) + '_' + str(scale[1])
            path = os.path.join(DIR, path)
            return path
    return ''

def isEmpty(path):
    path = path.strip()
    return len(path) == 0


def get_splash_tmp(packagename):
    type = get_config_value('test_type')
    if packagename == constants.KWAI_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/kwai/splash_tmp.png'
            path = os.path.join(DIR, path)
            if os.path.exists(path):
                return path
        elif type == "ios":
            path = 'tmp_img/ios/kwai/splash_tmp.png'
            path = os.path.join(DIR, path)
            if os.path.exists(path):
                return path

    return ''

def get_splash_tmp_dir(packagename, scale):
    type = get_config_value('test_type')
    dir = ''
    default_dir = ''
    if packagename == constants.KWAI_PACKAGENAME:
        if type == "android":
            default_dir = 'tmp_img/android/kwai/splash'
            dir = default_dir + str(scale[0]) + '_' + str(scale[1])
        elif type == "ios":
            default_dir = 'tmp_img/ios/kwai/splash'
            dir = default_dir + str(scale[0]) + '_' + str(scale[1])
    elif packagename == constants.TT_PACKAGENAME:
        if type == "android":
            default_dir = 'tmp_img/android/TT/splash'
            dir = default_dir + str(scale[0]) + '_' + str(scale[1])
        elif type == "ios":
            default_dir = 'tmp_img/ios/TT/splash'
            dir = default_dir + str(scale[0]) + '_' + str(scale[1])
    elif packagename == constants.SNACK_PACKAGENAME:
        if type == "android":
            default_dir = 'tmp_img/android/snack/splash'
            dir = default_dir + str(scale[0]) + '_' + str(scale[1])
        elif type == "ios":
            default_dir = 'tmp_img/ios/snack/splash'
            dir = default_dir + str(scale[0]) + '_' + str(scale[1])
    if os.path.exists(dir):
        dir = os.path.join(DIR, dir)
        return dir
    else:
        default_dir = os.path.join(DIR, default_dir)
        return default_dir

def get_tab_tmp(packagename):
    type = get_config_value('test_type')
    path = ''
    if packagename == constants.KWAI_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/kwai/kwaipro.png'
        elif type == "ios":
            path = 'tmp_img/ios/kwai/kwaipro.png'

    elif packagename == constants.TT_PACKAGENAME:
        if type == "android":
            path = 'tmp_img/android/TT/TT_tab.png'
        elif type == "ios":
            path = 'tmp_img/ios/TT/TT_tab.png'
    if os.path.exists(path):
        path = os.path.join(DIR, path)
        return path
    return ''


def get_tab_tmp_dir(packagename, scale):
    type = get_config_value('test_type')
    dir = ''
    default_dir = ''
    if packagename == constants.KWAI_PACKAGENAME:
        if type == constants.ANDROID:
            dir = 'tmp_img/android/kwai/tab/'  + str(scale[0]) + '_' + str(scale[1])
            default_dir = 'tmp_img/android/kwai/tab'
        elif type == constants.IOS:
            dir = 'tmp_img/ios/kwai/tab/'  + str(scale[0]) + '_' + str(scale[1])
            default_dir = 'tmp_img/ios/kwai/tab'

    elif packagename == constants.TT_PACKAGENAME:
        if type == constants.ANDROID:
            dir = 'tmp_img/android/TT/tab/'+ str(scale[0]) + '_' + str(scale[1])
            default_dir = 'tmp_img/android/TT/tab'
        elif type == constants.IOS:
            dir = 'tmp_img/ios/TT/tab/'+ str(scale[0]) + '_' + str(scale[1])
            default_dir = 'tmp_img/ios/TT/tab'

    elif packagename == constants.SNACK_PACKAGENAME:
        if type == constants.ANDROID:
            dir = 'tmp_img/android/snack/tab/'+ str(scale[0]) + '_' + str(scale[1])
            default_dir = 'tmp_img/android/snack/tab'
        elif type == constants.IOS:
            dir = 'tmp_img/ios/snack/tab/'+ str(scale[0]) + '_' + str(scale[1])
            default_dir = 'tmp_img/ios/snack/tab'
    if os.path.exists(dir):
        dir = os.path.join(DIR, dir)
        return dir
    else:
        default_dir = os.path.join(DIR, default_dir)
        return default_dir

# 获取识别特殊区域，视屏占位符的区域（y0,y1,x0,x1）
def get_process_roi(h, w):
    if get_config_value('pkg_name') == constants.KWAI_PACKAGENAME:
        if str(w) + '_' + str(h) == '600_1280':
            return (int(h / 3), int(h / 9 *5), int(w/3), int(w/3*2))
        elif str(w) + '_' + str(h) == '592_1280':
            #return (int(h / 3), int(h / 12 * 6), int(w/3), int(w/3 * 2))
            return (int(h / 3), int(h / 9 *5), int(w/3), int(w/3*2))
        else:
            return (int(h / 3), int(h / 9 *5), int(w/3), int(w/3*2))
    elif get_config_value('pkg_name') == constants.SNACK_PACKAGENAME:
        if str(w) + '_' + str(h) == '720_1280':
            return (int(h / 3), int(h / 3 * 2), int(w/3), int(w/3*2))
        elif str(w) + '_' + str(h) == '592_1280':
            #return (int(h / 3), int(h / 12 * 6), int(w/3), int(w/3 * 2))
            return (int(h / 3), int(h / 9 *5), int(w/3), int(w/3*2))
        else:
            return (int(h / 3), int(h / 3 * 2), int(w/3), int(w/3*2))