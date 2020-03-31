import numpy as np
from warnings import warn

xyz2srgb = np.array([[3.2404542, -1.5371385, -0.4985314],
                     [-0.9692660, 1.8760108, 0.0415560],
                     [0.0556434, -0.2040259, 1.0572252]])

srgb2xyz = np.array([[0.4124564, 0.3575761, 0.1804375],
                     [0.2126729, 0.7151522, 0.0721750],
                     [0.0193339, 0.1191920, 0.9503041]])

eps = 216 / 24389
kap = 24389 / 27


def _cart2polar_2pi(x, y):
    """convert cartesian coordinates to polar (uses non-standard theta range!)
    NON-STANDARD RANGE! Maps to ``(0, 2*pi)`` rather than usual ``(-pi, +pi)``
    """
    r, t = np.hypot(x, y), np.arctan2(y, x)
    t += np.where(t < 0., 2 * np.pi, 0)
    return r, t

def rgb2lch(rgb):
    arr = rgb @ srgb2xyz
    xyz_ref_white = [0.95047, 1.0, 1.08883]

    # scale by CIE XYZ tristimulus values of the reference white point
    arr /= xyz_ref_white

    # Nonlinear distortion and linear transformation
    mask = arr > eps
    arr[mask] = np.cbrt(arr[mask])
    arr[~mask] = (kap * arr[~mask] + 16.) / 116.

    x, y, z = arr[..., 0], arr[..., 1], arr[..., 2]

    # Vector scaling
    L = (116. * y) - 16.
    a = 500.0 * (x - y)
    b = 200.0 * (y - z)

    c, h = _cart2polar_2pi(a, b)

    return np.concatenate([x[..., np.newaxis] for x in [L, c, h]], axis=-1)

def lch2rgb(lch):
    lab = lch
    c, h = lab[..., 1], lab[..., 2]
    lab[..., 1], lab[..., 2] = c * np.cos(h), c * np.sin(h)

    L, a, b = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]
    y = (L + 16.) / 116.
    x = (a / 500.) + y
    z = y - (b / 200.)

    if np.any(z < 0):
        invalid = np.nonzero(z < 0)
        z[invalid] = 0

    xr = np.power(x, 3)
    xr[xr <= eps] = (116. * x[xr <= eps] - 16.) / kap

    lmask = L > (eps * kap)
    yr = y
    yr[lmask] = np.power((L[lmask] + 16.) / 116., 3)
    yr[~lmask] = L[~lmask] / kap

    zr = np.power(z, 3)
    zr[zr <= eps] = (116. * z[zr <= eps] - 16.) / kap

    xyz = np.dstack([xr, yr, zr])

    # rescale to the reference white (illuminant)
    xyz_ref_white = [0.95047, 1.0, 1.08883]
    xyz *= xyz_ref_white

    rgb = xyz @ xyz2srgb

    return rgb

def rgb2hsv(rgb):
    hsv = np.empty_like(rgb)

    # -- V channel
    v = rgb.max(-1)

    # -- S channel
    delta = rgb.ptp(-1)
    # Ignore warning for zero divided by zero
    old_settings = np.seterr(invalid='ignore')
    s = delta / v
    s[delta == 0.] = 0.

    # -- H channel
    # red is max
    idx = (rgb[:, :, 0] == v)
    hsv[idx, 0] = (rgb[idx, 1] - rgb[idx, 2]) / delta[idx]

    # green is max
    idx = (rgb[:, :, 1] == v)
    hsv[idx, 0] = 2. + (rgb[idx, 2] - rgb[idx, 0]) / delta[idx]

    # blue is max
    idx = (rgb[:, :, 2] == v)
    hsv[idx, 0] = 4. + (rgb[idx, 0] - rgb[idx, 1]) / delta[idx]

    h = hsv[:, :, 0] * 60.
    h[h < 0.] += 360.
    h[delta == 0.] = 0.

    np.seterr(**old_settings)

    # -- output
    hsv[:, :, 0] = h
    hsv[:, :, 1] = s
    hsv[:, :, 2] = v

    # remove NaN
    hsv[np.isnan(hsv)] = 0

    return hsv

def hsv2rgb(hsv):
    h = hsv[:, :, 0] / 60.
    v = hsv[:, :, 2]
    i = np.floor(h)
    f = h - i
    p = v * (1 - hsv[:, :, 1])
    q = v * (1 - f * hsv[:, :, 1])
    t = v * (1 - (1 - f) * hsv[:, :, 1])

    i = np.dstack((i, i, i)).astype(np.uint8)
    rgb = np.choose(i, [np.dstack((v, t, p)),
                        np.dstack((q, v, p)),
                        np.dstack((p, v, t)),
                        np.dstack((p, q, v)),
                        np.dstack((t, p, v)),
                        np.dstack((v, p, q))])

    return rgb
