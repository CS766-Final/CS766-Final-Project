import imageio as imio
import numpy as np
import color as clr


def hsv(rgb):
    for y in range(rgb.shape[0]):
        for x in range(rgb.shape[1]):
            pixel = rgb[y][x]

            max_ind = np.argmax(pixel)
            min_ind = np.argmin(pixel)
            med_ind = (3 - (max_ind + min_ind)) % 2

            clip = np.copy(pixel).clip(0.0, 1.0)

            h = 0
            if pixel[max_ind] != pixel[min_ind]:
                h = (pixel[med_ind] - pixel[min_ind]) / \
                    (pixel[max_ind] - pixel[min_ind])

            s = 0
            if clip[max_ind] != 0:
                s = 1.0 - (clip[min_ind] / clip[max_ind])

            pixel[med_ind] = pixel[max_ind] * (1.0 - s + s * h)
            pixel[min_ind] = pixel[max_ind] * (1.0 - s)

    return rgb


def lch(cam, cam2srgb):
    # Do the final color conversion
    srgb = cam @ cam2srgb

    srgb[srgb < 0] = 0

    lch = clr.rgb2lch(srgb)
    lch_c = clr.rgb2lch(np.clip(srgb, 0.0, 1.0))

    lch_r = np.concatenate([x[..., np.newaxis] for x in [
                           lch[:, :, 0], lch_c[:, :, 1], lch_c[:, :, 2]]], axis=-1)

    srgb_r = clr.lch2rgb(lch_r)

    cam_r = srgb_r @ np.linalg.inv(cam2srgb)

    return cam_r


def raw_to_rgb(path, wb_multipliers):
    '''
    Read in the raw image from the path and whitebalance the image

    Parameters
    ----------
    path : string
        the path to read from
    wb_multipliers : 3x3 matrix
        the white balance multipliers from the camera
    '''

    # read in the image
    # Convert each rgb value to [0,1]
    # 4095/3686 is the DNG whitelevel
    raw = np.clip(
        4095 / 3686 * np.divide(imio.imread(path, pilmode="RGB"), 255.0), 0.0, 1.0)
    # Make it brighter
    # This is so we can simulate clipping
    raw *= 1.33  # 0 EV boost
    # Ensure no value over 1
    clip = np.clip(raw, 0.0, 1.0)
    # White balance each pixel
    wb = clip @ wb_multipliers
    return wb


def write_img(img, path_to_write, cam2srgb, curve='srgb'):
    # Do the final color conversion
    img = img @ cam2srgb

    img[img < 0] = 0

    # Gamma correction
    # brings up all the mid range color
    # This is common practice when image is for monitor display

    img *= 4

    img = log(img) if curve == 'log' else np.power(img, 1. / 2.2)

    # Save
    imio.imwrite(path_to_write, np.uint8(np.clip(img * 255, 0, 255)))


def log(rgb):
    rgb[rgb < 0] = 0
    mask = rgb > 1
    rgb[mask] = 0.17883277 * np.log(rgb[mask] - 0.28466892) + 0.55991073
    rgb[~mask] = 0.5 * np.sqrt(rgb[~mask])
    return rgb


def get_cam_to_srgb(xyz_to_cam):
    # # Srgb color space to xyz
    # srgb_to_xyz = np.array([0.4124564, 0.3575761, 0.1804375, 0.2126729,
    #                         0.7151522, 0.0721750, 0.0193339, 0.1191920, 0.9503041])
    # srgb_to_xyz = srgb_to_xyz.reshape(3, 3)

    # # Single color map from srgb to camera
    # color_map = xyz_to_cam @ srgb_to_xyz

    # # Normalize the color map so each row sums to 1
    # color_map /= np.sum(color_map, axis=1)[:, np.newaxis]

    # # Invert and transpose the matrix so we can go from camera to srgb
    # cam2srgb = np.linalg.inv(color_map).T
    # # Print so we can hard code this and not compute everytime
    # # print(cam2srgb)

    cam2srgb = np.array([[1.56575239, -0.24745765, 0.02385829],
                         [-0.22562784, 1.70584814, -0.64032869],
                         [-0.34012454, -0.45839049, 1.6164704]])

    return cam2srgb


if __name__ == "__main__":
    # The wb values.
    # These were set on the camera
    wb_multipliers = np.diagflat(np.array([1.66122146, 1, 1.2102546]))

    # From the camera
    # Determines the mapping from xyz color space to the camera space
    xyz_to_cam = np.array([[1.28665438, -0.48895655, -0.08305354],
                           [-0.32054401,  1.10993317,  0.21061084],
                           [-0.12211477,  0.32127882,  0.76343939]])

    cam2srgb = get_cam_to_srgb(xyz_to_cam)

    wb = raw_to_rgb("./HSV/city_comp.png", wb_multipliers)

    # After whitebalancing, the image is normally just clipped again
    write_img(wb, "./ignore/sdr.png", cam2srgb)

    # This is what the image looks like after whitebalancing but not clipped
    write_img(wb, "./ignore/sdr_log.png", cam2srgb, 'log')

    # Do the hsv recovery
    hsv_hl = hsv(wb)
    # The image after hsv recovery
    write_img(hsv_hl, "./ignore/hsv_hl.png", cam2srgb, 'log')

    # Do the hsv recovery
    lch_hl = lch(wb, cam2srgb)
    # The image after hsv recovery
    write_img(lch_hl, "./ignore/lch_hl.png", cam2srgb, 'log')
