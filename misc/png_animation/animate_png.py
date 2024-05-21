from pathlib import Path
from argparse import ArgumentParser

import cv2
import numpy as np


def main():
    arg_parser = ArgumentParser('Animate png')
    arg_parser.add_argument('png', type=Path, help='Path to png')
    arg_parser.add_argument('save', type=Path, help='Path to save video')
    arg_parser.add_argument(
        '--direction',
        type=str,
        choices=[
            'up', 'down', 'rl', 'lr', 'diag', 'arcanoid',
            'arcanoid_random_speed', 'sinus', 'go_stay_go'
        ],
        default='diag',
        help='Move of png'
    )
    args = arg_parser.parse_args()
    assert args.png.is_file() and args.png.suffix.lower() == '.png', 'Wrong png'
    make_animation(args.png, args.save, args.direction)


def make_animation(png: Path, save: Path, direction: str):
    w, h = 1920, 1080
    fps = 30
    step_px = 10
    bg = 127 * np.ones((h, w, 3), dtype=np.uint8)
    assert direction in directions.keys(), 'Wrong direction'
    direction = directions[direction]
    overlay = cv2.imread(str(png), cv2.IMREAD_UNCHANGED)
    writer = cv2.VideoWriter(str(save), cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    for x, y in direction(w, h, step_px):
        frame = overlay_transparent(bg, overlay, int(x), int(y))
        writer.write(frame)
    writer.release()


def up(w, h, step):
    for y in np.arange(h, 0, -step):
        yield w / 2, y


def down(w, h, step):
    for y in np.arange(0, h, step):
        yield w / 2, y


def rl(w, h, step):
    for x in np.arange(0, w, step):
        yield x, h / 2


def lr(w, h, step):
    for x in np.arange(w, 0, -step):
        yield x, h / 2


def diag(w, h, step):
    ratio = step / (w*w + h*h)**0.5
    step_x, step_y = w * ratio, h * ratio
    for x, y in zip(np.arange(0, w, step_x), np.arange(0, h, step_y)):
        yield x, y


def arcanoid(w, h, step):
    x, y = np.random.randint(0, w), np.random.randint(0, h)
    offset_x, offset_y = 100, 100
    sinus = np.random.random()
    y_speed, x_speed = step * sinus, step * (1 - sinus)**0.5
    n_steps = 1000
    for _ in range(n_steps):
        yield x, y
        x, y = x + x_speed, y + y_speed
        if x + offset_x >= w or x <= 0:
            x = np.clip(x, 0, w - offset_x)
            x_speed *= -1
        if y + offset_y >= h or y <= 0:
            y = np.clip(y, 0, h - offset_y)
            y_speed *= -1


def arcanoid_random_speed(w, h, step):
    x, y = np.random.randint(0, w), np.random.randint(0, h)
    offset_x, offset_y = 100, 100
    sinus = np.random.random()
    y_speed, x_speed = step * sinus, step * (1 - sinus)**0.5
    n_steps = 1000
    for _ in range(n_steps):
        yield x, y
        x, y = x + x_speed, y + y_speed
        if x + offset_x >= w or x <= 0:
            x = np.clip(x, 0, w - offset_x)
            x_speed *= -1
        if y + offset_y >= h or y <= 0:
            y = np.clip(y, 0, h - offset_y)
            y_speed *= -1
        if np.random.random() < .1:
            scale_range = .8, 1.2
            scale = scale_range[0] + (scale_range[1] - scale_range[0])*np.random.random()
            x_speed, y_speed = x_speed * scale, y_speed * scale


def sinus(w, h, step):
    x, y = 0, h // 2
    offset_x = 100
    n_steps = 1000
    for _ in range(n_steps):
        yield x, y
        y = h//2 + 170*np.sin(x/150)
        x += step
        x_clipped = np.clip(x, 0, w - offset_x)
        if x_clipped != x:
            x = x_clipped
            step *= -1


def go_stay_go(w, h, step):
    ratio = step / (w * w + h * h) ** 0.5
    step_x, step_y = w * ratio, h * ratio
    for x, y in zip(np.arange(0, w // 2, step_x), np.arange(0, h // 2, step_y)):
        yield x, y
    for _ in range(0, 120):
        yield x, y
    for y in np.arange(h // 2, h, step):
        yield x, y


directions = {
    fun.__name__: fun
    for fun in [
        up, down, rl, lr, diag, arcanoid,
        arcanoid_random_speed, sinus, go_stay_go
    ]
}


def overlay_transparent(background, overlay, x, y):
    background = background.copy()

    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis=2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background


if __name__ == '__main__':
    main()
