import imageio as imio
import matplotlib.pyplot as plt
import numpy as np


def hsv(rgb):
    print(np.array(rgb[:][:]).shape)

    for y in range(rgb.shape[0]):
        for x in range(rgb.shape[1]):
            pixel = rgb[y][x]

            max_ind = np.argmax(pixel)
            min_ind = np.argmin(pixel)
            med_ind = (3-(max_ind+min_ind)) % 2

            clipped_pixel = np.copy(pixel).clip(0.0, 1.0)

            h = 0
            if pixel[max_ind] != pixel[min_ind]:
                h = (pixel[med_ind] - pixel[min_ind]) / \
                    (pixel[max_ind] - pixel[min_ind])
            # elif clipped_pixel[max_ind] != clipped_pixel[min_ind]:
            #     h = (clipped_pixel[med_ind] - clipped_pixel[min_ind]) / \
            #         (clipped_pixel[max_ind] - clipped_pixel[min_ind])

            s = 0
            if clipped_pixel[max_ind] != 0:
                s = 1.0 - (clipped_pixel[min_ind]/clipped_pixel[max_ind])

            pixel[med_ind] = pixel[max_ind] * (1.0 - s + s * h)
            pixel[min_ind] = pixel[max_ind] * (1.0 - s)

    return rgb


def lch(rgb):
    raise NotImplementedError


def raw_to_rgb(path):
    # The wb values.
    # These were set on the camera
    wb_multipliers = np.diagflat(np.array([1.2282886, 1, 1.6131868]))

    # read in the image
    # Convert each rgb value to [0,1]
    raw = np.divide(imio.imread(path, pilmode="RGB"), 255.0)
    # Make it brighter
    # This is so we can simulate clipping
    raw *= 1.5
    # Ensure no value over 1
    clip = np.clip(raw, 0.0, 1.0)
    # White balance each pixel
    wb = clip @ wb_multipliers
    return wb


def write_img(img, path_to_write):
    # From the camera
    # Determines the mapping from xyz color space to the camera space
    xyz_to_cam = np.array([1.4868945, -0.6438222, -0.0699355, -0.261274,
                           1.0494869, 0.1399011, -0.1775877, 0.313115, 0.4792254])
    xyz_to_cam = xyz_to_cam.reshape(3, 3)

    # Srgb color space to xyz
    srgb_to_xyz = np.array([0.4124564,  0.3575761, 0.1804375, 0.2126729,
                            0.7151522, 0.0721750, 0.0193339,  0.1191920, 0.9503041])
    srgb_to_xyz = srgb_to_xyz.reshape(3, 3)

    # Single color map from srgb to camera
    color_map = xyz_to_cam @ srgb_to_xyz

    # Normalize the color map so each row sums to 1
    color_map /= np.sum(color_map, axis=1)[:, np.newaxis]

    # Invert the matrix so we can go from camera to srgb
    color_map = np.linalg.inv(color_map)

    # Do the final color conversion
    img = img @ color_map

    print(np.max(img))
    img = img/np.max(img)

    # Gamma correction
    # brings up all the mid range color
    # This is common practice when image is for monitor display
    img = np.power(img, 1/2.2)

    # img = log(img)

    # Save
    imio.imwrite(path_to_write, img)


def log(rgb):
    return 0.29325513 * np.log10(1.01091561573 * rgb + 0.01091561572) + 0.6695992135


if __name__ == "__main__":

    wb = raw_to_rgb("./HSV/city_comp.png")
    write_img(wb, "./ignore/WB.png")

    hsv_extraction_img = hsv(wb)
    write_img(hsv_extraction_img, "./ignore/HSV_extraction.png")
