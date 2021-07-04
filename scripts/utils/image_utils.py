import numpy as np
from skimage.color import rgb2gray

def np_binarize(img):
    """
    Turns an image into a binary 0-1 image based on whether the colors exceed a threshold
    Args:
        img: A numpy ndarray image
    Returns:
        A binary image with all pixels having either 0 or 1 value
    """
    thresh = 0.95
    return 1.0 * (img > thresh)


def crop_and_clean_img(img, center_x, center_y, side_len):
    """
    Crops an image centered around a point, converts it to grayscale, and binarizes it to simplify processing
    Args:
        img: A numpy ndarray image
        center_x: The x coord of the center of the desired cropped region
        center_y: The y coord of the center of the desired cropped region
        side_len: The length of a side of the desired cropped region
    Returns:
        A cleaned, cropped, binary image with all pixels having either 0 or 1 value
    """
    half_side_len = int(side_len / 2)
    crop_img = img[center_y - half_side_len:center_y + half_side_len, center_x - half_side_len:center_x + half_side_len]
    clean_img = np_binarize(rgb2gray(crop_img))
    return clean_img


def get_color_similarity(img, rgb, color_diff_thresh=30):
    """
    Returns how similar a region of an image is to a certain color
    Args:
        img: A numpy ndarray representing part of an image
        rgb: A list/tuple of length 3 representing an rgb color
        color_diff_thresh: A threshold that does the following: If the sum of difference in color exceeds 3x this, that pixel is a mismatch.
    Returns:
        The proportion of pixels (0-1) in the image that match the color rgb
    """

    color = np.array(rgb)
    diff_img = 1.0 * (np.sum(abs(img - color), 2) < color_diff_thresh * 3)
    size = diff_img.size
    sum_img = np.sum(diff_img)
    return sum_img / size
    

def is_1080p_img(img):
    (m, n, _) = img.shape
    return m == 1080 and n == 1920