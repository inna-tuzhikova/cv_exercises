import argparse
import os
import shutil

import cv2
import numpy as np


def save_image(image, file_path):
    cv2.imwrite(file_path, image)


def gen_image(shape, h, w):
    def get_random_color():
        return tuple(map(int, np.random.randint(0, 255, size=3)))

    fill_prob = 0.5
    fill = np.random.uniform() < fill_prob
    thickness = -1 if fill else 1

    w, h = max(20, w), max(20, h)
    background = np.ones(shape=(h, w, 3)) * np.array(get_random_color())
    background = background.astype(np.uint8)
    color = get_random_color()
    if shape == 'circle':
        radius = np.random.randint(min(10, int(0.1 * min(w, h))),
                                   int(0.4 * min(w, h)))
        center = tuple(np.random.randint(radius, size - radius) for size in [w, h])

        img = cv2.circle(background, center, radius, color, thickness=thickness, lineType=cv2.LINE_AA)
    elif shape == 'square':
        pt_1 = tuple(np.random.randint(0, int(0.95 * size)) for size in [w, h])
        offset = np.random.randint(int(0.05 * min(w, h)),
                                   max(2, min(w - pt_1[0], h - pt_1[1])))
        pt_2 = (pt_1[0] + offset, pt_1[1] + offset)
        img = cv2.rectangle(background, pt_1, pt_2, color, thickness=thickness, lineType=cv2.LINE_AA)
    elif shape == 'rectangle':
        pt_1 = tuple(np.random.randint(0, int(0.95 * size)) for size in [w, h])
        pt_2 = (np.random.randint(pt_1[0] + 0.05 * w, w),
                np.random.randint(pt_1[1] + 0.05 * h, h))
        img = cv2.rectangle(background, pt_1, pt_2, color, thickness=thickness, lineType=cv2.LINE_AA)
    elif shape in ['triangle', 'pentagon', 'hexagon']:
        n_pts = 3 if shape == 'triangle' else 5 if shape == 'pentagon' else 6
        radius = np.random.randint(min(10, int(0.1 * min(w, h))),
                                   int(0.5 * min(w, h)))
        center = tuple(np.random.randint(radius, size - radius) for size in [w, h])
        if n_pts == 3:
            alphas = np.random.uniform(0, 2 * np.pi, size=n_pts)
        else:
            # Regular polygon angles
            alphas = np.random.uniform(0, 2 * np.pi) + np.array([i * 2*np.pi/n_pts for i in range(n_pts)])
            # Make it less regular (random may collapse to smaller n_vertices)
            alphas += np.random.uniform(-np.pi/6, np.pi/6, size=n_pts)
            # Scale to (0, 2*pi) - otherwise self-intersections may occur
            alphas = np.sort(alphas - 2*np.pi * np.floor(alphas / np.pi / 2))
        pts = center + radius * np.array([(np.cos(alpha), np.sin(alpha)) for alpha in alphas])
        if fill:
            img = cv2.fillPoly(background, [pts.reshape(-1, 1, 2).astype(np.int32)],
                               color, lineType=cv2.LINE_AA)
        else:
            img = cv2.polylines(background, [pts.reshape(-1, 1, 2).astype(np.int32)],
                                True, color, thickness=thickness, lineType=cv2.LINE_AA)
    else:
        img = background
    return img


def _main_(args):
    shapes = list(set(args.shapes))
    h, w = args.size
    save_dir = args.save_dir
    n = args.n_img

    f_name_format = '%s_%0' + str(len(str(n)) + 1) + 'd.jpg'

    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
        except Exception as e:
            print('Unable to create save dir: %s. %s' % (save_dir, e))
            return
    elif os.path.isfile(save_dir):
        print('Save_dir is file')
        return
    else:
        try:
            shutil.rmtree(save_dir)
        except Exception as e:
            print('Save_dir  already exist. Unable to delete save dir: %s. %s' % (save_dir, e))
            return

    for shape in shapes:
        shape_dir = os.path.join(save_dir, shape)
        try:
            os.makedirs(shape_dir)
        except Exception as e:
            print('Unable to create shape dir: %s. %s' % (shape_dir, e))
            return
        for i in range(n):
            img = gen_image(shape, h, w)
            save_image(img, os.path.join(shape_dir, f_name_format % (shape, i + 1)))
        print('%s images saved: %s' % (shape.capitalize(), shape_dir))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Script generates shapes images into separate folders')
    argparser.add_argument(
        '-shapes',
        dest='shapes',
        required=True,
        choices=['circle', 'triangle', 'rectangle', 'square', 'pentagon', 'hexagon'],
        nargs='+',
        help='List of shapes to gen')
    argparser.add_argument(
        '-n_img',
        default=100,
        type=int,
        dest='n_img',
        help='number of images'
    )
    argparser.add_argument(
        '-size',
        default=[256, 256],
        nargs=2,
        type=int,
        dest='size',
        help='size of an image')
    argparser.add_argument(
        '-save_dir',
        default='tmp',
        dest='save_dir',
        help='dir to save images')

    args = argparser.parse_args()
    _main_(args)
