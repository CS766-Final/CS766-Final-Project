import color as clr
import numpy as np

def lch(cam, cam2srgb):
    # Do the final color conversion
    srgb = cam @ cam2srgb

    srgb[srgb < 0] = 0

    lch = clr.rgb2lch(srgb)
    lch_c = clr.rgb2lch(np.clip(cam, 0, 1) @ cam2srgb)

    l = lch[:, :, 0]
    lc = lch_c[:, :, 0]
    l[l < lc] = lc[l < lc]

    lch_r = np.concatenate([x[..., np.newaxis] for x in [
        l, lch_c[:, :, 1], lch[:, :, 2]]], axis=-1)

    srgb_r = clr.lch2rgb(lch_r)

    mat = np.linalg.inv(cam2srgb)

    cam_r = srgb_r @ mat

    return cam_r