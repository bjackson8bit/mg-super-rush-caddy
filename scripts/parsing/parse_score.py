from skimage import io
from skimage.color import rgb2gray
from skimage.util.dtype import img_as_ubyte
from scripts.utils.sprite_parsing import Spritesheet, find_most_similar
from scripts.utils.image_utils import crop_and_clean_img, get_color_similarity, is_1080p_img
from scripts.utils.path import get_resource_abs_path
from skimage.transform import resize

player_y_spacing = 157
orange = [243,136,6]
red = [224,2,32]
green = [16,226,110]
yellow = [248,218,8]
blue = [8,83,236]
player_colors = [blue, red, green, yellow]

minus_plus_spritesheet = Spritesheet(sheet=rgb2gray(io.imread(get_resource_abs_path('minus_plus_3col_46x46.png'))), \
    num_sprites=3, num_cols=3, sprite_width=46, sprite_height=46, sprite_names=[-1, 0, 1])

result_digit_spritesheet = Spritesheet(sheet=rgb2gray(io.imread(get_resource_abs_path('result_digits_5col_66x66.png'))), \
    num_sprites=10, num_cols=5, sprite_width=66, sprite_height=66, sprite_names=[*range(10)])


def result_to_string(res):
    """
    Turns an integer into a string representing score (has a + or - sign)
    Args:
        res: An int representing score
    Returns:
        A string representing the player's score
    """    
    if res > 0:
        return f"+{str(res)}"
    elif res == 0:
        return "E"
    else:
        return str(res)


def get_results_data(img):
    """
    Gets player scores from a results screen and orders them by the true player index, not their standings. (ie, player 1 will appear 1st even if they are in last)
    Args:
        img: A ndarray numpy image representing a results screen
    Returns:
        A list of integers representing the scores (under/over par) of players 1-4
    """
    img_1080p = img_as_ubyte(resize(img, (1080, 1920), anti_aliasing=True))
    player_mapping = get_player_order_mapping(img_1080p)
    if not player_mapping:
        return None
    scores = [get_player_data_from_results(i, img_1080p) for i in range(len(player_mapping))]
    if any(s is None for s in scores):
        return None
    return [scores[player_mapping[idx]] for idx in range(len(player_mapping))]


def get_player_data_from_results(i, img):
    """
    Gets the results score of a particular index on the results screen.
    Args:
        i: A player index (0-3)
        img: A 1080p ndarray numpy image representing a results screen
    Returns:
        An integer representing the player at index i's score.
    """
    sign_match_thresh = 0.75
    sign_y_center_init = 365
    sign_y_center = sign_y_center_init + i * player_y_spacing
    sign_x_center_2digit = 1409
    sign_x_center_1digit = 1439
    sign_side_len = 46

    digit_match_thresh = 0.6
    digit_side_len = 66
    digit_y_center_init = 358
    digit_y_center = digit_y_center_init + i * player_y_spacing

    clean_sign = crop_and_clean_img(img, sign_x_center_2digit, sign_y_center, sign_side_len)
    sign, score = find_most_similar(clean_sign, minus_plus_spritesheet)
    # print(f"{i} {sign} {score}")
    # 2 digit score
    if score > sign_match_thresh:
        digit_x_center_init = 1465
        if sign == 0:
            return 0

        if sign == -1:
            neg_offset = 10
            digit_x_center_init -= neg_offset
        
        clean_digit_1 = crop_and_clean_img(img, digit_x_center_init, digit_y_center, digit_side_len)
        digit1, score = find_most_similar(clean_digit_1, result_digit_spritesheet)
        # print(f"{str(digit1)} {score}")
        if score < digit_match_thresh:
            print(f"Unable to recognize digit 1 of player {i+1}'s score")
            return None
        # io.imshow(clean_digit_1)
        # io.show()

        clean_digit_2 = crop_and_clean_img(img, digit_x_center_init + digit_side_len - 4, digit_y_center, digit_side_len)
        digit2, score = find_most_similar(clean_digit_2, result_digit_spritesheet)
        if score < digit_match_thresh:
            print(f"Unable to recognize digit 2 of player {i+1}'s score")
            return None
        # print(f"{str(digit2)} {score}")
        # io.imshow(clean_digit_2)
        # io.show()

        return sign * (10 * digit1 + digit2)
    # 1 digit score
    else:
        digit_x_center_init = 1495
        clean_sign = crop_and_clean_img(img, sign_x_center_1digit, sign_y_center, sign_side_len)
        sign, score = find_most_similar(clean_sign, minus_plus_spritesheet)
        # print(f"{i} {sign} {score}")

        if score < sign_match_thresh:
            print(f"Unable to recognize sign (+,-,+/-) of player {i+1}'s score")
            return None
            
        if sign == 0:
            return 0
        if sign == -1:
            neg_offset = 10
            digit_x_center_init -= neg_offset
        
        clean_digit = crop_and_clean_img(img, digit_x_center_init, digit_y_center, digit_side_len)
        digit, score = find_most_similar(clean_digit, result_digit_spritesheet)
        if score < digit_match_thresh:
            print(f"Unable to recognize digit 1 of player {i+1}'s score")
            return None
        # print(f"{str(digit)} {score}")
        return sign * digit


def is_results_screen(img):
    """
    Determines if the input image is a golf after-hole results screen.
    Args:
        img: A ndarray numpy image representing a results screen
    Returns:
        True if the input array is a results screen, False otherwise
    """
    orange = [243,136,6]
    white = [255,255,255]
    # coords for 1080p
    header_x, header_y = 850, 205
    header_width, header_height = 250, 45
    header_2_x = 1405
    white_x, white_y_init = 250, 258
    white_width, white_height = 1400, 32
    thresh = 0.95
    p_y_spacing = player_y_spacing
    if not is_1080p_img(img):
        (m, n, _) = img.shape
        x_scale = n / 1920
        y_scale = m / 1080 
        header_x, header_y = int(header_x * x_scale), int(header_y * y_scale)
        header_width, header_height = int(header_width * x_scale), int(header_height * y_scale)
        header_2_x = int(header_2_x * x_scale)
        white_x, white_y_init = int(white_x * x_scale), int(white_y_init * y_scale)
        white_width, white_height = int(white_width * x_scale), int(white_height * y_scale)
        p_y_spacing = player_y_spacing * y_scale

    sim = get_color_similarity(img[header_y:header_y+header_height,header_x:header_x+header_width], orange)
    if sim < thresh:
        return False
    sim = get_color_similarity(img[header_y:header_y+header_height,header_2_x:header_2_x+header_width], orange)
    if sim < thresh:
        return False
    for i in range(4):
        white_y = white_y_init + round(i * p_y_spacing)
        sim = get_color_similarity(img[white_y:white_y+white_height,white_x:white_x+white_width], white)
        if sim < thresh:
            return False
    return True


def get_player_order_mapping(img):
    """
    Maps from actual player number to their index of appearance on the results screen
    Args:
        img: A 1080p ndarray numpy image representing a results screen
    Returns:
        A dict mapping from players 0-3 to the index of appearance on the results screen.
    """
    thresh = 0.65
    player_x = 1080
    player_y_init = 310
    player_width = 70
    player_height = 90

    player_mapping = {}

    used_set = set()

    for i in range(4):
        player_y = player_y_init + i * player_y_spacing
        crop_img = img[player_y:player_y+player_height,player_x:player_x+player_width]
        for idx, color in enumerate(player_colors):
            if idx in used_set:
                continue
            sim = get_color_similarity(crop_img, color)
            if sim > thresh: 
                player_mapping[idx] = i
                used_set.add(idx)
                break
    for i in range(len(used_set)):
        if i not in used_set:
            return None
    return player_mapping