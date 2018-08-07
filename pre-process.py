import os
import zipfile
from multiprocessing import Pool

import cv2 as cv
from tqdm import tqdm

from config import identity_annot_filename, image_folder, img_size
from utils import ensure_folder, get_bbox


def extract(folder):
    filename = '{}.zip'.format(folder)
    print('Extracting {}...'.format(filename))
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('data')


def check_one_image(line):
    line = line.strip()
    if len(line) > 0:
        tokens = line.split(' ')
        image_name = tokens[0].strip()
        bbox = bboxes[image_name]
        filename = os.path.join(image_folder, image_name)
        try:
            image_bgr = cv.imread(filename)
            image_rgb = cv.cvtColor(image_bgr, cv.COLOR_BGR2RGB)
            x1, y1, w, h = bbox
            image_rgb = image_rgb[y1:y1 + h, x1:x1 + w]
            image_rgb = cv.resize(image_rgb, (img_size, img_size), cv.INTER_CUBIC)
        except cv.error as err:
            print(err)
            print(filename)


def check_image():
    with open(identity_annot_filename, 'r') as file:
        lines = file.readlines()
    pool = Pool(24)
    for _ in tqdm(pool.imap_unordered(check_one_image, lines), total=len(lines)):
        pass
    pool.close()
    pool.join()


if __name__ == '__main__':
    # parameters
    ensure_folder('data')

    if not os.path.isdir(image_folder):
        extract(image_folder)

    bboxes = get_bbox()
    check_image()
