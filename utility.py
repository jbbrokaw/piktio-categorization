from __future__ import unicode_literals
import numpy as np


def transparency_cleanup(image_data, threshhold=0.5):
    """Clean an image with transparent pixels by replacing them with
    white color"""
    (width, height, colors) = image_data.shape
    if colors != 4:
        raise TypeError('Requires a RGBA file (4 columns)')

    new_image = np.array(image_data[:, :, :3])

    for i in xrange(width):
        for j in xrange(height):
            if image_data[i, j, 3] < threshhold:
                new_image[i, j] = [1.0, 1.0, 1.0]

    return new_image


def bin_key(color_key, threshhold=0.2):
    """'Smoothes' colors by rounding (binning) floats RGB values into
    0, 0.1, 0.2, ...."""
    bins = 1.0 / threshhold
    if int(bins) != bins:
        raise ValueError("threshhold must divide 1.0 evenly")
    else:
        bins = int(bins)

    rounded_key = np.array(color_key)
    for i in xrange(color_key.shape[0]):
        bin = int(round(color_key[i] / threshhold))
        rounded_color = float(bin) / float(bins)
        rounded_key[i] = rounded_color
    return tuple(rounded_key)


def num_colors(image_data, threshhold=0.2):
    """Return the number of colors in an RGB or RGBA image numpy array
    in image_data. relevant_digits refers to rounding to avoid counting tiny
    variations in color (1 is 0.1, 2 is 0.01, etc.)"""
    (width, height, colors) = image_data.shape  # Must be at least RGB
    if colors == 4:
        image_data = transparency_cleanup(image_data)

    color_dict = dict()

    for i in xrange(width):
        for j in xrange(height):
            color_key = bin_key(image_data[i, j], threshhold)
            color_dict[color_key] = color_dict.setdefault(color_key, 0) + 1

    return len(color_dict)

if __name__ == '__main__':
    from boto.s3.connection import OrdinaryCallingFormat
    import boto
    import io
    import skimage.io

    virtual_file = io.BytesIO()

    s3_conn = boto.connect_s3(calling_format=OrdinaryCallingFormat())
    s3_conn.get_bucket('pikts.piktio.com')
    pikts = s3_conn.get_bucket('pikts.piktio.com')
    pikt_list = pikts.get_all_keys()
    for pikt in pikt_list[:10]:
        pikt.get_contents_to_file(virtual_file)
        virtual_file.seek(0)
        pikt_data = skimage.io.imread(virtual_file)
        virtual_file.seek(0)
        print num_colors(pikt_data, 0.25)
