import numpy as np
import cv2
import sys
import time
import os
import shutil


video_save_path = 'example.avi'
pic_save_dir = 'images'
n_frames = 200
test_time = 10  # sec
w, h = 1920, 1080


def get_white_noise(h, w):
    n_channels = 3
    return np.random.uniform(0, 256, size=(h, w, n_channels)).astype(np.uint8)


def save_image(image, path):
    cv2.imwrite(path, image)


def ensure_dir(dir_path):
    if os.path.exists(pic_save_dir):
        shutil.rmtree(pic_save_dir)
    try:
        os.makedirs(pic_save_dir)
    except Exception as e:
        print('Unable to create dir %s.\n%s' % (dir_path, e))
        sys.exit(1)


def get_dir_size(dir_path):
    size = 0
    for dirpath, _, filenames in os.walk(dir_path):
        for f in filenames:
            file_path = os.path.join(dirpath, f)
            if not os.path.islink(file_path):
                size += os.path.getsize(file_path)
    return size


def main():
    video_writer = cv2.VideoWriter(video_save_path, cv2.VideoWriter_fourcc(*'MPEG'), 25., (w, h))
    start = time.time()
    print('Video')
    while True:
        video_writer.write(get_white_noise(h, w))
        elapsed = time.time() - start
        if elapsed >= test_time:
            break
        sys.stdout.write('\r')
        sys.stdout.write('Elapsed: %0.1f sec' % elapsed)
        sys.stdout.flush()
    video_writer.release()
    print('\nVideo: {:,} bytes'.format(os.path.getsize(video_save_path)))

    ensure_dir(pic_save_dir)
    print('\nImages')
    idx = 0
    start = time.time()
    while True:
        save_image(get_white_noise(h, w), os.path.join(pic_save_dir, 'image_%05d.png' % (idx + 1)))
        elapsed = time.time() - start
        if elapsed >= test_time:
            break
        idx += 1
        sys.stdout.write('\r')
        sys.stdout.write('Elapsed: %0.1f sec' % elapsed)
        sys.stdout.flush()
    print('\nImages: {:,} bytes'.format(get_dir_size(pic_save_dir)))


if __name__ == '__main__':
    main()
    time.time()
