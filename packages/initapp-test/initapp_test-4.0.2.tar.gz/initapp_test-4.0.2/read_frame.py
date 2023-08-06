import ffmpeg._ffmpeg as ffmpeg
import ffmpeg._probe as ffprobe
import numpy
import cv2
import os,sys
import random


def read_frame_by_time(in_file, time):
    """
    指定时间节点读取任意帧
    """
    out, err = (
        ffmpeg.input(in_file, ss=time)
              .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
              .run(capture_stdout=True)
    )
    return out

def scale_video(in_file, out_file):
    out, err = (
        ffmpeg.input(in_file)
            .output(out_file)
            .run(capture_stdout=True)
    )
    return out, err

def read_frame_by_time1(in_file, time, out_file):
    """
    指定时间节点读取任意帧
    """
    out, err = (
        ffmpeg.input(in_file, ss=time)
            .output(out_file, vframes='1', f='image2', vcodec='mjpeg')
            .run(capture_stdout=True)
    )
    return out, err


def get_video_info(in_file):
    """
    获取视频基本信息
    """
    try:
        probe = ffprobe.probe(in_file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            print('No video stream found', file=sys.stderr)
            sys.exit(1)
        return video_stream
    except ffprobe.Error as err:
        print(str(err.stderr, encoding='utf8'))
        sys.exit(1)

if __name__ == '__main__':
    file_path = "555.mp4"
    video_info = get_video_info(file_path)
    total_duration = video_info['duration']
    float_time = float(total_duration)
    print('总时间：' + total_duration + 's')
    cut_couts = int(float_time * 10)
    time_offset = 0
    for index in range(cut_couts):
        time_offset += float(total_duration)/10
    # random_time = random.randint(1, int(float(total_duration)) - 1) + random.random()
    # print('随机时间：' + str(random_time) + 's')
        out = read_frame_by_time(file_path, time_offset)
        image_array = numpy.asarray(bytearray(out), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    #cv2.imshow('frame', image)
    #cv2.waitKey()
        cv2.imwrite("{}.jpg".format(str(index)), image)
