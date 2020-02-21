import imageio as imio
import numpy as np


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


def lch(rgb):
    raise NotImplementedError


def raw_to_rgb(path):
    # The wb values.
    # These were set on the camera
    wb_multipliers = np.diagflat(np.array([1.66122146, 1, 1.2102546]))

    # read in the image
    # Convert each rgb value to [0,1]
    raw = np.clip(4095 / 3686 * np.divide(imio.imread(path, pilmode="RGB"), 255.0), 0.0, 1.0)
    # Make it brighter
    # This is so we can simulate clipping
    raw *= 1.33  # 0 EV boost
    # Ensure no value over 1
    clip = np.clip(raw, 0.0, 1.0)
    # White balance each pixel
    wb = clip @ wb_multipliers
    return wb


def write_img(img, path_to_write):
    # # From the camera
    # # Determines the mapping from xyz color space to the camera space
    # xyz_to_cam = np.array([1.4868945, -0.6438222, -0.0699355, -0.261274,
    #                        1.0494869, 0.1399011, -0.1775877, 0.313115, 0.4792254])
    # xyz_to_cam = xyz_to_cam.reshape(3, 3)
    #
    # # Srgb color space to xyz
    # srgb_to_xyz = np.array([0.4124564, 0.3575761, 0.1804375, 0.2126729,
    #                         0.7151522, 0.0721750, 0.0193339, 0.1191920, 0.9503041])
    # srgb_to_xyz = srgb_to_xyz.reshape(3, 3)
    #
    # # Single color map from srgb to camera
    # color_map = xyz_to_cam @ srgb_to_xyz
    #
    # # Normalize the color map so each row sums to 1
    # color_map /= np.sum(color_map, axis=1)[:, np.newaxis]
    #
    # # Invert the matrix so we can go from camera to srgb
    # color_map = np.linalg.inv(color_map)

    cam2srgb = np.array([[1.56575239, -0.24745765, 0.02385829],
                        [-0.22562784, 1.70584814, -0.64032869],
                        [-0.34012454, -0.45839049, 1.6164704]])

    # Do the final color conversion
    img = img @ cam2srgb

    img = img / np.max(img)

    img[img < 0] = 0

    # Gamma correction
    # brings up all the mid range color
    # This is common practice when image is for monitor display
    img = np.power(img, 1. / 2.2)

    # img = log(img)

    # Save
    imio.imwrite(path_to_write, img)


def log(rgb):
    return np.where(rgb[:][:] > 0.0149480,
                    0.2756705 * np.log10(5.5555556 * rgb[:][:] + 0.0280665) + 0.4150634,
                    5.9861078 * rgb[:][:] + 0.0625265)


if __name__ == "__main__":
    wb = raw_to_rgb("./city_comp.png")
    write_img(wb, "../ignore/WB.png")

    hsv_hl = np.where(wb >= 1.0, hsv(wb), wb)
    write_img(hsv_hl, "../ignore/hsv_hl.png")
