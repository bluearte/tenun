"""

"""

import logging

import OpenImageIO as oiio

from . import images


logger = logging.getLogger(__name__)


def create(
        width: int,
        height: int, 
        nchannel: int = 4, 
        fmt: oiio.TypeDesc = oiio.UINT8
    ) -> oiio.ImageBuf:
    """
        Create an instance of ImageBuf
    """
    spc = oiio.ImageSpec(width, height, nchannel, fmt)
    img_buf = oiio.ImageBuf(spc)
    return img_buf


def duplicate(src: oiio.ImageBuf) -> oiio.ImageBuf:
    """
        Duplicate an ImageBuf
    """

    src_spc = src.spec()

    buf_pixels = src.get_pixels()
    new_buf = oiio.ImageBuf(src_spc)
    new_buf.set_pixels(src.roi, buf_pixels)

    return new_buf


def convert_colorspace(src: oiio.ImageBuf, from_space: str, to_space: str, **kwargs) -> oiio.ImageBuf:
    """
        Convert color space
    """
    src_spc = src.spec()

    if src_spc.channel_bytes() < 2:
        logger.debug("Skipping conversion of color space of 8-bit image")
        return src

    if not to_space:
        logger.debug("Skipping conversion. to_space parameter is undefined")
        return src

    if not from_space:
        img_cs = src.spec().getattribute("oiio:ColorSpace")
        if not img_cs:
            logger.debug("Skipping conversion. No color space found")
            return src

        logger.debug("Use color space from image: %s", img_cs)
        from_space = img_cs

    if from_space == to_space:
        logger.debug("Skipping color space conversion because source and output is same")
        return src

    extra_kwargs = {"nthreads": 1, "unpremult": True}
    extra_kwargs.update(kwargs)

    cc_buf = oiio.ImageBuf()
    oiio.ImageBufAlgo.colorconvert(cc_buf, src, from_space, to_space, **extra_kwargs)

    return cc_buf


def re_size(src: oiio.ImageBuf, width: int = 0, height: int = 0, **kwargs) -> oiio.ImageBuf:
    """
        Resize ImageBuf
    """
    src_spc = src.spec()
    src_width = src_spc.width
    src_height = src_spc.height

    if width == 0:
        width = src_width

    if height == 0:
        height = src_height

    if width == 0 and height == 0:
        return src

    if width == src_width and height == src_height:
        return src

    extra_kwargs = {"nthreads": 1}
    extra_kwargs.update(kwargs)

    resized_spc = oiio.ImageSpec(src_spc)
    resized_spc.width = width
    resized_spc.height = height

    # create empty ImageBuf
    resized_buf = oiio.ImageBuf()
    if not oiio.ImageBufAlgo.resize(resized_buf, src, roi=resized_spc.roi, **kwargs):
        logger.error(resized_buf.geterror())

    return resized_buf


def re_format(src: oiio.ImageBuf, width: int = 0, height: int = 0, mode: str = "fit", **kwargs) -> oiio.ImageBuf:
    """
        Resize ImageBuf and maintain aspect ratio
    """
    modes = ("fit", "fill", "width", "height")
    if mode not in modes:
        str_modes = ", ".join(modes)
        raise ValueError(f"Unsupported mode {mode}. Supported modes are {str_modes}")

    src_spc = src.spec()
    src_width = src_spc.width
    src_height = src_spc.height

    if width == 0:
        width = src_width

    if height == 0:
        height = src_height

    if width == src_width and height == src_height:
        return src

    extra_kwargs = {"nthreads": 1}
    extra_kwargs.update(kwargs)

    if mode in ("width", "fit"):
        dst_buf = _reformat_fit(src, width=width, height=height, **kwargs)
        return dst_buf

    if mode in ("height", "fill"):
        dst_buf = _reformat_fill(src, width=width, height=height, **kwargs)
        return dst_buf

    return src


def _reformat_fit(src, width, height, **kwargs):
    spc = src.spec()
    padded_spc = oiio.ImageSpec(spc)
    padded_spc.width = width
    padded_spc.height = height

    # create empty ImageBuf
    padded_buf = oiio.ImageBuf()

    if not oiio.ImageBufAlgo.fit(padded_buf, src, roi=padded_spc.roi, **kwargs):
        logger.error(padded_buf.geterror())

    return padded_buf


def _reformat_fill(src, width, height, **kwargs):
    src_spc = src.spec()
    src_width = src_spc.width
    src_height = src_spc.height

    ratio_width = width / src_width
    ratio_height = height / src_height

    ratio_fill = max(ratio_width, ratio_height)

    resized_width = int(src_width * ratio_fill)
    resized_height = int(src_height * ratio_fill)

    resized_spc = oiio.ImageSpec(src_spc)
    resized_spc.width = resized_width
    resized_spc.height = resized_height

    resized_buf = oiio.ImageBuf()
    oiio.ImageBufAlgo.resize(resized_buf, src, roi=resized_spc.roi, **kwargs)

    x_offset = (resized_width - width) // 2
    y_offset = (resized_height - height) // 2

    cropped_roi = oiio.ROI(x_offset, x_offset + width, y_offset, y_offset + height)
    cropped_buf = oiio.ImageBufAlgo.crop(resized_buf, roi=cropped_roi, **kwargs)
    cropped_buf.set_full(cropped_buf.roi.xbegin,
                            cropped_buf.roi.xend,
                            cropped_buf.roi.ybegin,
                            cropped_buf.roi.yend,
                            0,
                            1)

    return cropped_buf
