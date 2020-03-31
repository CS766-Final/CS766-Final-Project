import rawpy
import imageio
import numpy as np
import os
from p_tqdm import p_umap
import hsv
import lch


def unpack(raw):
    """
    Unpack raw data to white-balanced RGB image and relevant color metadata to
    transform camera RGB to sRGB

    Parameters
    ----------
    raw : ndarray
        rawpy object representation of raw image file
    """

    black = raw.black_level_per_channel.copy()
    wb = np.diagflat(raw.camera_whitebalance.copy()[:-1])
    cam2rgb = raw.color_matrix.copy()[:, :-1]
    cfa = raw.raw_image.copy().astype(float)
    mask = raw.raw_colors.copy()

    # scale cfa to valid range
    scale(cfa, mask, black)
    rgb = binning(cfa, mask)

    # simulate camera ADC gain stage
    rgb = gain(rgb, 0)

    # white balance
    rgb = rgb @ wb

    return rgb, cam2rgb


def scale(img, mask, black):
    """
    Scale 10b image from [black, 1023] -> [0, 1]

    Parameters
    ----------
    img : ndarray
        2D representation of CFA data
    mask : ndarray
        2D matrix same size as img, determines RGBG color
        R = 0, G1 = 1, B = 2, G2 = 3
    black: ndarray
        Contains black level for each color in CFA
    """

    masks = [mask == 0,
             mask == 1,
             mask == 3,
             mask == 2]

    for i in range(4):
        m = masks[i]
        b = black[i]
        a = 1 / (1023.0 - b)
        img[m] = a * (img[m] - b)


def deinterleave(img, mask):
    """
    Extract RGBG values into three separate matrices R, G, B.
    Performs first binning step in size reduction

    Parameters
    ----------
    img : ndarray
        2D representation of CFA data
    mask : ndarray
        2D matrix same size as img, determines RGBG color
        R = 0, G1 = 1, B = 2, G2 = 3
    """

    # generate shape for first 2x2 bin
    s = (int(img.shape[0] / 2), int(img.shape[1] / 2))

    # there are two green channels in CFA
    # average them for first binning step
    g = np.mean([img[mask == 1], img[mask == 3]], axis=0).reshape(s)

    # extract remaining channels
    r = np.reshape(img[mask == 0], s)
    b = np.reshape(img[mask == 2], s)

    return r, g, b


def binning(img, mask):
    """
    Perform pixel binning on input image with respect to
    given color channel and return stacked RGB m x n x c
    matrix

    Parameters
    ----------
    img : ndarray
        2D representation of CFA data
    mask : ndarray
        2D matrix same size as img, determines RGBG color
        R = 0, G1 = 1, B = 2, G2 = 3
    """

    # get individual channels, dims are halved from full img
    r, g, b = deinterleave(img, mask)

    # generate shapes for next 2x2 bin step
    s = (int(r.shape[0] / 2), int(r.shape[1] / 2))
    shape = (s[0], r.shape[0] // s[0],
             s[1], r.shape[1] // s[1])

    # do final bin step
    r.reshape(shape).mean(-1).mean(1)
    g.reshape(shape).mean(-1).mean(1)
    b.reshape(shape).mean(-1).mean(1)

    # stack depth-wise to create RGB matrix
    rgb = np.dstack((r, g, b))
    return rgb


def write_img(img, path, cam2rgb, curve='power', hdr=False):
    """

    """
    # clip to prevent pink highlights in SDR image
    img = img if hdr else np.clip(img, 0, 1)

    # Do the final color conversion
    img = img @ cam2rgb.T
    img[img < 0] = 0

    # Gamma correction
    # brings up all the mid range color
    # This is common practice when image is for monitor display

    img *= np.power(2, 0)

    # HLG or power curve.
    img = arrilog(img) if curve == 'log' else np.power(img, 1. / 2.2)
    # Save
    imageio.imwrite(path, np.uint8(np.clip(img * 255, 0, 255)))


def process(path, name):
    """
    Performs entire camera pipe on image with all highlight recovery methods
    and writes them in respective directories

    Parameters
    ----------
    name : str
        filename
    """

    filename = os.path.splitext(name)[0]

    with rawpy.imread(path) as raw:
        # unpack raw data
        rgb, cam2rgb = unpack(raw)

        # After white balancing, the image is normally just clipped again
        write_img(rgb, f'../ignore/output/sdr/{filename}.png', cam2rgb)

        # This is what the image looks like after white balancing but not clipped
        write_img(rgb, f'../ignore/output/sdr_log/{filename}.png', cam2rgb, 'log')

        # Write hsv recovery
        write_img(hsv.hsv(rgb), f'../ignore/output/hsv/{filename}.png', cam2rgb, 'log', True)

        # Write lch recovery
        write_img(lch.lch(rgb, cam2rgb), f'../ignore/output/lch/{filename}.png', cam2rgb, 'log', True)


def thread(filename):
    filepath = '../ignore/input' + os.sep + filename
    if filepath.endswith(".dng"):
        process(filepath, filename)


def gain(lin, ev):
    """
    Performs gain adjustment on image given a number of photograpic stops

    Parameters
    ----------
    lin : ndarray
        RGB image
    ev : double
        Scalar value in units of photographic stops to adjust by
    """
    return np.clip(lin * np.power(2, ev), 0.0, 1.0)


def encode(lin):
    """
    Protune 12EV log encoding

    Parameters
    ----------
    lin : ndarray
        RGB image
    """
    b = 400
    a = b - 1
    return np.log(a * lin + 1) / np.log(b)


def arrilog(scene):
    """
   ARRI Log-C 800EI log encoding

   Parameters
   ----------
   lin : ndarray
       RGB image
   """
    rgb = scene.copy()
    rgb[rgb < 0] = 0
    mask = rgb > 0.010591
    rgb[mask] = 0.247190 * np.log10(5.555556 * rgb[mask] + 0.052272) + 0.385537
    rgb[~mask] = 5.367655 * rgb[~mask] + 0.092809
    return rgb


if __name__ == "__main__":
    for subdir, dirs, files in os.walk('../ignore/input'):
        p_umap(thread, files)
