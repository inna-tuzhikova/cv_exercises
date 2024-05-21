import argparse
import os
import shutil
import random

import cv2
import numpy as np


N_CHANNELS = 1


letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
fonts = [cv2.FONT_HERSHEY_DUPLEX, cv2.FONT_HERSHEY_PLAIN,
         cv2.FONT_HERSHEY_COMPLEX, cv2.FONT_HERSHEY_COMPLEX_SMALL,
         cv2.FONT_HERSHEY_TRIPLEX, cv2.FONT_ITALIC]

random_params = {
    'easy': {'color_range': 255,
             'letters': letters,
             'screen_percent_range': 0.8,
             'center_shift_range': 0.5,
             'angle_range': 0,
             'fonts': [cv2.FONT_HERSHEY_PLAIN]
             },
    'medium': {'color_range': (100, 255),
             'letters': letters,
             'screen_percent_range': (0.4, 0.6),
             'center_shift_range': (0.4, 0.6),
             'angle_range': (-10, 10),
             'fonts': fonts[: 3]
             },
    'hard': {'color_range': (50, 255),
             'letters': letters,
             'screen_percent_range': (0.2, 0.8),
             'center_shift_range': (0.3, 0.7),
             'angle_range': (-15, 15),
             'fonts': fonts
             },
    'insane': {'color_range': (30, 255),
             'letters': letters + letters.lower(),
             'screen_percent_range': (0.2, 0.8),
             'center_shift_range': (0.2, 0.8),
             'angle_range': (-15, 15),
             'fonts': fonts
             }
}



def save_image(image, file_path):
    cv2.imwrite(file_path, image)


def gen_image(h, w, mode):
    def get_random_color(color_range):
        if isinstance(color_range, int):
            color = color_range
        elif isinstance(color_range, tuple):
            color = np.random.randint(*color_range)
        else:
            color = 0
        return (color, color, color)

    w, h = max(32, w), max(32, h)
    background = np.zeros(shape=(h, w, N_CHANNELS))
    background = background.astype(np.uint8)

    letter = random.choice(random_params[mode]['letters'])
    color = get_random_color(random_params[mode]['color_range'])
    image = background

    # Approx percent along the screen axis
    size_range = random_params[mode]['screen_percent_range']
    size = size_range if isinstance(size_range, float) else np.random.uniform(*size_range)

    # Diff % left or lower the letter
    shift_range = random_params[mode]['center_shift_range']
    shift_x, shift_y = (shift_range, shift_range) if isinstance(shift_range, float) \
        else np.random.uniform(*shift_range, size=2)

    angle_range = random_params[mode]['angle_range']
    angle = angle_range if isinstance(angle_range, int) else np.random.uniform(*angle_range)

    font = np.random.choice(random_params[mode]['fonts'])
    font_size = np.min([size * w / cv2.getTextSize(letter, font, 1, 1)[0][0],
                        size * h / cv2.getTextSize(letter, font, 1, 1)[0][1]])

    new_size = cv2.getTextSize(letter, font, font_size, 1)
    try:
        cv2.putText(image,
                    letter,
                    org=(
                        np.round(shift_x * (w - new_size[0][0])).astype(np.int32),
                        np.round(h - shift_y * (image.shape[0] - new_size[0][1])).astype(np.int32)
                    ),
                    fontFace=font,
                    fontScale=font_size,
                    color=color,
                    thickness=1,
                    lineType=cv2.LINE_AA)
    except Exception as e:
        print(e)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1)
    image = cv2.warpAffine(image, M, (w, h))

    return image, letter


def _main_(args):
    h, w = args.size
    save_dir = args.save_dir
    n = args.n_img
    mode = args.mode

    f_name_format = 'letter_%0' + str(len(str(n)) + 1) + 'd_%s.jpg'

    if os.path.exists(save_dir) and os.path.isdir(save_dir):
        try:
            shutil.rmtree(save_dir)
        except Exception as e:
            print('Save_dir already exist. Unable to delete save dir: %s. %s' % (save_dir, e))
            return
    elif os.path.exists(save_dir) and os.path.isfile(save_dir):
        print('Save_dir is file')
        return
    try:
        os.makedirs(save_dir)
    except Exception as e:
        print('Unable to create save dir: %s. %s' % (save_dir, e))
        return

    for i in range(n):
        image, letter = gen_image(h, w, mode)
        save_image(image, os.path.join(save_dir, f_name_format % (i + 1, letter)))
    print('%d images saved to %s' % (n, save_dir))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Script generates letters images into separate folders')
    argparser.add_argument(
        '-n_img',
        default=100,
        type=int,
        dest='n_img',
        help='number of images'
    )
    argparser.add_argument(
        '-mode',
        default='easy',
        choices=['easy', 'medium', 'hard', 'insane'],
        type=str,
        dest='mode',
        help='Level of classification difficulty'
    )
    argparser.add_argument(
        '-size',
        default=[32, 32],
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
