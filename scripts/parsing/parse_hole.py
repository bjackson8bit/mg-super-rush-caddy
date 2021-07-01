from skimage import io
from skimage.color import rgb2gray
from skimage.util.dtype import img_as_ubyte
from scripts.utils.sprite_parsing import Spritesheet, find_most_similar, get_similarity
from scripts.utils.image_utils import crop_and_clean_img, is_1080p_img
from scripts.utils.path import get_resource_abs_path
from skimage.transform import resize


h_for_hole_1080p = rgb2gray(io.imread(get_resource_abs_path('h_1080p.png')))

h_for_hole_720p = rgb2gray(io.imread(get_resource_abs_path('h_720p.png')))

hole_digit_spritesheet = Spritesheet(sheet=rgb2gray(io.imread(get_resource_abs_path('hole_digits_5col_24x24.png'))), \
    num_sprites=10, num_cols=5, sprite_width=24, sprite_height=24, sprite_names=[*range(10)])


def is_hole_screen(img):
    if not is_1080p_img(img):
        hole_center_1digit_x = 53
        hole_side_len = 16
        hole_center_2digit_x = 46
        hole_banner_y = 32
        h_for_hole = h_for_hole_720p
        thresh = 0.6
    else:
        hole_center_1digit_x = 80
        hole_side_len = 24
        hole_center_2digit_x = 69
        hole_banner_y = 48
        h_for_hole = h_for_hole_1080p
        thresh = 0.8

    img_1_digit_hole = crop_and_clean_img(img, hole_center_1digit_x, hole_banner_y, hole_side_len)

    img_2_digit_hole = crop_and_clean_img(img, hole_center_2digit_x, hole_banner_y, hole_side_len)

    sim_1 = get_similarity(h_for_hole, img_1_digit_hole)
    sim_2 = get_similarity(h_for_hole, img_2_digit_hole)
    # print(f"{sim_1}, {sim_2}")
    return sim_1 > thresh or sim_2 > thresh


def get_hole_data(img):
    hole_center_1digit_x = 80
    hole_side_len = 24
    hole_center_2digit_x = 69
    hole_banner_y = 48
    digit_side_len = 24
    digit_thresh = .7 if is_1080p_img(img) else .6
    img_1080p = img_as_ubyte(resize(img, (1080, 1920), anti_aliasing=True))

    h_for_hole = h_for_hole_1080p

    img_1_digit_hole = crop_and_clean_img(img_1080p, hole_center_1digit_x, hole_banner_y, hole_side_len)

    img_2_digit_hole = crop_and_clean_img(img_1080p, hole_center_2digit_x, hole_banner_y, hole_side_len)

    sim_1 = get_similarity(h_for_hole, img_1_digit_hole)
    sim_2 = get_similarity(h_for_hole, img_2_digit_hole)

    thresh = 0.8 if is_1080p_img(img) else 0.65

    if sim_1 < thresh and sim_2 < thresh:
        return None
    elif sim_2 > sim_1:
        digit_2_x = 172
        clean_digit_2 = crop_and_clean_img(img_1080p, digit_2_x, hole_banner_y, digit_side_len)
        digit2, score = find_most_similar(clean_digit_2, hole_digit_spritesheet)
        if score < digit_thresh:
            print('Unable to get hole number')
            return None
        return 10 + digit2
    else:
        digit_1_x = 161
        clean_digit_1 = crop_and_clean_img(img_1080p, digit_1_x, hole_banner_y, digit_side_len)
        digit1, score = find_most_similar(clean_digit_1, hole_digit_spritesheet)
        if score < digit_thresh:
            print('Unable to get hole number')
            return None
        return digit1