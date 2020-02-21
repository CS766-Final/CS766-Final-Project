import numpy as np
from warnings import warn

srgb2xyz = np.array([[0.4124564, 0.3575761, 0.1804375],
                     [0.2126729, 0.7151522, 0.0721750],
                     [0.0193339, 0.1191920, 0.9503041]])


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
    arr = arr / xyz_ref_white

    # Nonlinear distortion and linear transformation
    mask = arr > 0.008856
    arr[mask] = np.cbrt(arr[mask])
    arr[~mask] = 24389/(27 * 116) * arr[~mask] + 16. / 116.

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
        warn('Color data out of range: Z < 0 in %s pixels' % invalid[0].size,
             stacklevel=2)
        z[invalid] = 0

    xyz = np.dstack([x, y, z])

    mask = xyz > 0.2068966
    xyz[mask] = np.power(xyz[mask], 3.)
    xyz[~mask] = (xyz[~mask] - 16.0 / 116.) / (24389/(27 * 116))

    # rescale to the reference white (illuminant)
    xyz_ref_white = [0.95047, 1.0, 1.08883]
    xyz *= xyz_ref_white

    rgb = xyz @ np.linalg.inv(srgb2xyz)

    return rgb
