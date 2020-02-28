import color as clr
import numpy as np

def hsv(rgb):
    hsv = clr.rgb2hsv(rgb)
    hsv_c = clr.rgb2hsv(np.clip(rgb, 0.0, 1.0))

    hsv_r = np.concatenate([x[..., np.newaxis] for x in [
        hsv_c[:, :, 0], hsv_c[:, :, 1], hsv[:, :, 2]]], axis=-1)

    rgb = clr.hsv2rgb(hsv_r)

    return rgb