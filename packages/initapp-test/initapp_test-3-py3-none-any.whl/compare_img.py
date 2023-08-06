import cv2
import numpy as np

HIST_SIMULARITY = 85
HASH_SIMULARITY = 2
"""
值哈希算法、差值哈希算法和感知哈希算法都是值越小，相似度越高，取值为0-64，即汉明距离中，64位的hash值有多少不同。 三直方图和单通道直方图的值为0-1，值越大，相似度越高。
"""

# 均值哈希算法
def aHash(img):
    # 缩放为8*8
    img = cv2.resize(img, (8, 8))
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # s为像素和初值为0，hash_str为hash值初值为''
    s = 0
    hash_str = ''
    # 遍历累加求像素和
    for i in range(8):
        for j in range(8):
            s = s + gray[i, j]
    # 求平均灰度
    avg = s / 64
    # 灰度大于平均值为1相反为0生成图片的hash值
    for i in range(8):
        for j in range(8):
            if gray[i, j] > avg:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


# 差值感知算法
def dHash(img):
    # 缩放8*8
    img = cv2.resize(img, (9, 8))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


# 感知哈希算法(pHash)
def pHash(img, isgray):
    # 缩放32*32
    img = cv2.resize(img, (32, 32))  # , interpolation=cv2.INTER_CUBIC

    # 转换为灰度图
    if isgray == False:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(img))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]

    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash


# 通过得到RGB每个通道的直方图来计算相似度
def classify_hist_with_split(image1, image2, size=(256, 256)):
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


# 计算单通道的直方图的相似值
def calculate(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


# Hash值对比
def cmpHash(hash1, hash2):
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1)!=len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n

# 像素对比
def cmpPix(image1, image2):
    n = 0
    img1 = cv2.imread(image1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2, cv2.IMREAD_GRAYSCALE)
    all_pix = 0
    height, width = img1.shape
    for line in range(height):
        for pixel in range(width):
            if img1[line][pixel] == img2[line][pixel]:
                n = n + 1
            all_pix += 1
    print(n)
    print(all_pix)
    return n / all_pix

# imagepath1 = 'imagedir/10.jpg'
# imagepath2 = 'imagedir/11.jpg'
# img1 = cv2.imread(imagepath1)  #  11--- 16 ----13 ---- 0.43
# img2 = cv2.imread(imagepath2)

# img1 = cv2.imread('imagedir/0.jpg')  #  10----11 ----8------0.25
# img2 = cv2.imread('imagedir/1.jpg')
#
# img1 = cv2.imread('imagedir/0.jpg')  #  6------5 ----2--------0.84
# img2 = cv2.imread('imagedir/1.jpg')
#
# img1 = cv2.imread('imagedir/0.jpg')  #    14------19---10--------0.70
# img2 = cv2.imread('imagedir/1.jpg')
#
# img1 = cv2.imread('imagedir/0.jpg')  #    39------33---18--------0.58
# img2 = cv2.imread('imagedir/1.jpg')

# hash1 = aHash(img1)
# hash2 = aHash(img2)
# n = cmpHash(hash1, hash2)
# print('均值哈希算法相似度：', n)
#
# hash1 = dHash(img1)
# hash2 = dHash(img2)
# n = cmpHash(hash1, hash2)
# print('差值哈希算法相似度：', n)
#
# hash1 = pHash(img1)
# hash2 = pHash(img2)
# n = cmpHash(hash1, hash2)
# print('感知哈希算法相似度：', n)
#
# n = classify_hist_with_split(img1, img2)
# print('三直方图算法相似度：', n)
#
# n = cmpPix(imagepath1, imagepath2)
# print('像素对比：', n)

# 感知hash 比较两图片相似度
def cmppHash(imagepath1, imagepath2):
    img1 = cv2.imread(imagepath1)  # 11--- 16 ----13 ---- 0.43
    img2 = cv2.imread(imagepath2)
    hash1 = pHash(img1, False)
    hash2 = pHash(img2, False)
    n = cmpHash(hash1, hash2)
    if n >= HASH_SIMULARITY:
        return False
    else:
        return True

# 感知hash 比较两图片相似度
def cmppHash1(image1, image2, isgray):
    hash1 = pHash(image1, isgray)
    hash2 = pHash(image2, isgray)
    n = cmpHash(hash1, hash2)
    if n >= HASH_SIMULARITY:
        return False
    else:
        return True

# 差值哈希算法 比较两图片相似度
def cmpdHash(imagepath1, imagepath2):
    img1 = cv2.imread(imagepath1)  # 11--- 16 ----13 ---- 0.43
    img2 = cv2.imread(imagepath2)
    hash1 = dHash(img1)
    hash2 = dHash(img2)
    n = cmpHash(hash1, hash2)
    if n > HASH_SIMULARITY:
        return False
    else:
        return True


# 均值哈希算法 比较两图片相似度
def cmpaHash(imagepath1, imagepath2):
    img1 = cv2.imread(imagepath1)  # 11--- 16 ----13 ---- 0.43
    img2 = cv2.imread(imagepath2)
    hash1 = aHash(img1)
    hash2 = aHash(img2)
    n = cmpHash(hash1, hash2)
    if n > HASH_SIMULARITY:
        return False
    else:
        return True


# 直方图相似度
def cmpHist(imagepath1, imagepath2):
    img1 = cv2.imread(imagepath1)  # 11--- 16 ----13 ---- 0.43
    img2 = cv2.imread(imagepath2)
    n = classify_hist_with_split(img1, img2)
    return n * 100 > HIST_SIMULARITY

# 像素对比相似度：
def cmpPix1(imagepath1, imagepath2):
    n = cmpPix(imagepath1, imagepath2)
    return n > HIST_SIMULARITY