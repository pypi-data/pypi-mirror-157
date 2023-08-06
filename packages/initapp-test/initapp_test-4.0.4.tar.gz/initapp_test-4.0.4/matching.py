# 基于FLANN的匹配器(FLANN based Matcher)定位图片
import numpy as np
import cv2
import os
import tmp_image_utils
import math
import compare_img

MIN_MATCH_COUNT = 50  # 设置最低特征点匹配数量为10

def match(tmp_image_path, imagepath):

    template = cv2.imread(tmp_image_path, 0)  # queryImage
    target = cv2.imread(imagepath, 0)  # trainImage
    # Initiate SIFT detector创建sift检测器
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        # src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        # dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # # 计算变换矩阵和MASK
        # M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        # matchesMask = mask.ravel().tolist()
        # h, w = template.shape
        # # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        # pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        # dst = cv2.perspectiveTransform(pts, M)
        # cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
        return True
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
        return False

def match2(template, target, ratio, MIN_MATCH_COUNT):

    #template = cv2.imread(tmp_image_path, 0)  # queryImage
    #target = cv2.imread(imagepath, 0)  # trainImage
    # Initiate SIFT detector创建sift检测器
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)

    if len(kp2) < 10:
        return False
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < ratio * n.distance:
            good.append(m)
    if len(good) >= MIN_MATCH_COUNT:
        # 获取关键点的坐标
        # src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        # dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # # 计算变换矩阵和MASK
        # M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        # matchesMask = mask.ravel().tolist()
        # h, w = template.shape
        # # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        # pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        # dst = cv2.perspectiveTransform(pts, M)
        # cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
        return True
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
        return False

# 视屏loading占位图出现
def match_vedio_load(tmp_image_path, imagepath):
    if tmp_image_path == '':
        return False
    if os.path.isdir(tmp_image_path):
        match  = False
        for f in os.listdir(tmp_image_path):
            tmp_p = os.path.join(tmp_image_path, f)
            if os.path.isfile(tmp_p):
                tmp_img = cv2.imread(tmp_p, 0)  # 原图为彩色图，可将第二个参数变为0，为灰度图
                img = cv2.imread(imagepath, 0)

                tmp_img = __process_tmp(tmp_img)
                img = __process_tmp(img)
                match = compare_img.cmppHash1(tmp_img, img, True)

                cv2.imshow('frame', img)
                cv2.imshow('frame1', tmp_img)
                cv2.waitKey()
                cv2.destroyAllWindows()

            if match:
                return True

    else:
        tmp_img = cv2.imread(tmp_image_path, 0)  # 原图为彩色图，可将第二个参数变为0，为灰度图
        img = cv2.imread(imagepath, 0)

        tmp_img = __process_tmp(tmp_img)
        img = __process_tmp(img)
        match = compare_img.cmppHash1(tmp_img, img, True)
        cv2.imshow('frame', img)
        cv2.imshow('frame1', tmp_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return match


def sift(img):
    #img = cv2.imread(filename) # 读取文件
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 转化为灰度图
    sift = cv2.SIFT_create()
    keyPoint, descriptor = sift.detectAndCompute(img, None) # 特征提取得到关键点以及对应的描述符（特征向量）
    return keyPoint, descriptor


def surf(img):
    # img = cv2.imread(filename) # 读取文件
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 转化为灰度图
    sift = cv2.SIFT_create()
    keyPoint, descriptor = sift.detectAndCompute(img, None) # 特征提取得到关键点以及对应的描述符（特征向量）
    return keyPoint, descriptor


def orb(img):
    # img = cv2.imread(filename) # 读取文件
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 转化为灰度图
    sift = cv2.ORB_create()
    keyPoint, descriptor = sift.detectAndCompute(img, None) # 特征提取得到关键点以及对应的描述符（特征向量）
    return keyPoint, descriptor


def match1(img, target, method, ratio, min_count_rate, min_match_count):
    #matches = []
    knnMatches = None
    min_count = min_match_count
    if(method == 'sift'):
        kp1, des1 = sift(img)
        kp2, des2 = sift(target)
        #bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)  # sift的normType应该使用NORM_L2或者NORM_L1
        #matches = bf.match(des1, des2)
        #matches = sorted(matches, key=lambda x: x.distance)
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        if len(kp2) < 2:
            return False
        min_count = min(len(kp1), len(kp2))
        knnMatches = flann.knnMatch(des1, des2, k=2)  # drawMatchesKnn

    if (method == 'surf'):
        kp1, des1 = surf(img)
        kp2, des2 = surf(target)
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)  # surf的normType应该使用NORM_L2或者NORM_L1
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        knnMatches = bf.knnMatch(des1, des2, k=1)  # drawMatchesKnn
    if(method == 'orb'):
        kp1, des1 = orb(img)
        kp2, des2 = orb(target)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True) # orb的normType应该使用NORM_HAMMING
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        knnMatches = bf.knnMatch(des1, des2, k = 1) # drawMatchesKnn
    # 过滤

    good = []
    # 舍弃大于0.7的匹配
    for m, n in knnMatches:
        if m.distance < ratio * n.distance:
            good.append(m)
    min_count = min_count * min_count_rate
    if min_count < min_match_count:
        min_count = min_match_count
    if len(good) >= min_count:
        # 获取关键点的坐标
        # src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        # dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # # 计算变换矩阵和MASK
        # M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        # matchesMask = mask.ravel().tolist()
        # h, w = template.shape
        # # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        # pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        # dst = cv2.perspectiveTransform(pts, M)
        # cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
        return True
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
        return False


def corn_match(tmppath, imagepath):
    if tmppath == '':
        return False

    tmp_img = cv2.imread(tmppath, 0)  # 原图为彩色图，可将第二个参数变为0，为灰度图
    img = cv2.imread(imagepath, 0)

    h_t, w_t = tmp_img.shape[:2]
    h_img, w_img = img.shape[:2]


    mask_tmp = np.zeros_like(tmp_img)
    roi_tmp = tmp_image_utils.get_process_roi(h_t, w_t)

    mask_tmp[roi_tmp[0]:roi_tmp[1],roi_tmp[2]:roi_tmp[3]] = 255 #y0:y1, x0:x1

    roi_img = tmp_image_utils.get_process_roi(h_img, w_img)
    mask_img = np.zeros_like(img)
    mask_img[roi_img[0]:roi_img[1],roi_img[2]:roi_img[3]] = 255 #y0:y1, x0:x1
    tmp_corners = cv2.goodFeaturesToTrack(tmp_img, 500, 0.01, 0.1, mask=mask_tmp)  # 返回的结果是 [[ a., b.]] 两层括号的数组。


    img_corners = cv2.goodFeaturesToTrack(img, 500, 0.01, 0.1, mask=mask_img)  # 返回的结果是 [[ a., b.]] 两层括号的数组。
    if img_corners is None or len(img_corners) < 200:
        return False

    tmp_corners = np.int0(tmp_corners)
    img_corners = np.int0(img_corners)

    # index = min(len(tmp_corners), len(img_corners))
    # for i in range(index):
    #     #print("tmp:", tmp_corners[i].ravel())
    #     #print("img:", img_corners[i].ravel())
    #     cv2.circle(tmp_img, tmp_corners[i].ravel(), 3, (255, 255, 0))
    #     cv2.circle(img, tmp_corners[i].ravel(), 3, (255, 255, 0))

    #将角点画在图片上
    radius_rate = min(float(h_img / h_t), float(w_img / w_t))
    # cv2.circle(tmp_img, i.ravel(), int(3 * radius_rate), (255, 255, 0))
    for i in tmp_corners:
        cv2.circle(tmp_img, i.ravel(), 5, (255, 255, 0), thickness=-1)
    for i in img_corners:
        cv2.circle(img, i.ravel(), math.ceil(5), (255, 255, 0), thickness=-1)

    # tmp_img = __process_tmp(tmp_img)
    # img = __process_tmp(img)

    match = match2(tmp_img, img, 0.5, 12)

    #math123 = compare_img.cmppHash1(tmp_img, img, True)


    return match
    # #
    # cv2.imshow('frame', img)
    # cv2.imshow('frame1', tmp_img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    #
    #
    #
    # goods = []
    # for i in tmp_corners:
    #     x, y = i.ravel()
    #     for j in img_corners:
    #         x1, y1 = j.ravel()
    #         if x==x1 and y == y1:
    #             goods.append(i)
    #
    # return len(goods) >= len(tmp_corners) * 0.5

def corn_match2(tmppath, imagepath, match_count, match_ratio):
    if tmppath == '':
        return False

    tmp_img = cv2.imread(tmppath, 0)  # 原图为彩色图，可将第二个参数变为0，为灰度图
    img = cv2.imread(imagepath, 0)

    h_t, w_t = tmp_img.shape[:2]
    h_img, w_img = img.shape[:2]


    mask_tmp = np.zeros_like(tmp_img)
    roi_tmp = tmp_image_utils.get_process_roi(h_t, w_t)

    mask_tmp[roi_tmp[0]:roi_tmp[1],roi_tmp[2]:roi_tmp[3]] = 255 #y0:y1, x0:x1

    roi_img = tmp_image_utils.get_process_roi(h_img, w_img)
    mask_img = np.zeros_like(img)
    mask_img[roi_img[0]:roi_img[1],roi_img[2]:roi_img[3]] = 255 #y0:y1, x0:x1
    tmp_corners = cv2.goodFeaturesToTrack(tmp_img, 50, 0.1, 5, mask=mask_tmp)  # 返回的结果是 [[ a., b.]] 两层括号的数组。


    img_corners = cv2.goodFeaturesToTrack(img, 50, 0.1, 5, mask=mask_img)  # 返回的结果是 [[ a., b.]] 两层括号的数组。
    if img_corners is None:
        return False

    tmp_corners = np.int0(tmp_corners)
    img_corners = np.int0(img_corners)

    __process_tmp(tmp_img)
    __process_tmp(img)

    # index = min(len(tmp_corners), len(img_corners))
    # for i in range(index):
    #     #print("tmp:", tmp_corners[i].ravel())
    #     #print("img:", img_corners[i].ravel())
    #     cv2.circle(tmp_img, tmp_corners[i].ravel(), 3, (255, 255, 0))
    #     cv2.circle(img, tmp_corners[i].ravel(), 3, (255, 255, 0))

    for i in tmp_corners:
        cv2.circle(tmp_img, i.ravel(), 3, (255, 255, 0))
    for i in img_corners:
        cv2.circle(img, i.ravel(), 3, (255, 255, 0))

    #match = match2(tmp_img, img, 0.6, 10)
    match = match2(tmp_img, img, match_ratio, match_count)
    return match

# 有多个模版tmp
def corn_match_tmps(tmp_path, imagepath):
    if tmp_path == '':
        return False
    if os.path.isdir(tmp_path):
        match  = False
        for f in os.listdir(tmp_path):
            tmp_p = os.path.join(tmp_path, f)
            if os.path.isfile(tmp_p):
                match = corn_match(tmp_p, imagepath)
            if match:
                return True

    else:
        match = corn_match(tmp_path, imagepath)

    return match





def __process_tmp(image):
    h, w = image.shape[:2]
    roi = tmp_image_utils.get_process_roi(h, w)
    tmp = image[roi[0]:roi[1], roi[2]:roi[3]].copy()
    image[0:h, 0:w] = 255
    image[roi[0]:roi[1], roi[2]:roi[3]] = tmp
    return tmp
    # image[0:roi[0], 0:w] = 255
    # image[roi[1]:h, 0:w] = 255

# 图片特定区域内变化
def __not_change(image):
    #a = np.var(image[int(h/3):int(h/7 * 4),0:w])
    #a1 = np.mean(image[int(h/3):int(h/7 * 4),0:w])
    #标准差
    std = np.std(image)
    #极差
    ptp = np.ptp(image)
    #灰度图中色值极差<10 && 标准差 < 5 任务整个区域变化不大，是一张纯色图
    return ptp < 10 and std < 5

def roi_not_change(image, ptp_threshold, std_threshold):
    #a = np.var(image[int(h/3):int(h/7 * 4),0:w])
    #a1 = np.mean(image[int(h/3):int(h/7 * 4),0:w])
    #标准差
    std = np.std(image)
    #极差
    ptp = np.ptp(image)
    #灰度图中色值极差<10 && 标准差 < 5 任务整个区域变化不大，是一张纯色图
    return ptp < ptp_threshold and std < std_threshold


if __name__ == '__main__':
    #tmp_image_utils.get_vedio_tmp_img_dir('com.kwai.video', )
    #corn_match('tmp_img/android/kwai/vediotmp/vedio_load_tmp.jpg', 'imagedir/335.jpg')
    match_vedio_load('tmp_img/android/kwai/vediotmp/vedio_load_tmp.jpg', 'imagedir/191.jpg')
    #__is_change(cv2.imread('imagedir/132.jpg', 0))