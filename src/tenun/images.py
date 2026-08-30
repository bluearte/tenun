"""
"""

import pathlib
import typing

import OpenImageIO as oiio

from . import buffers


def get_channels(src: str) -> typing.List[typing.List[str]]:
    inp = oiio.ImageInput.open(src)
    spc = inp.spec()

    layers = []
    idx = 0
    for ch in spc.channelnames:
        names = ch.split(".")
        if len(names) == 1:
            layer = "main"
        else:
            layer = ".".join(names[:-1])

        if not layers:
            layers.append([layer, [ch]])

        else:
            if layer in layers[idx]:
                layers[idx][-1].append(ch)

            if layer not in layers[idx]:
                idx += 1
                layers.append([layer, [ch]])

    inp.close()
    return layers


def extract_channel(src: str, channel_name: str) -> oiio.ImageBuf:
    inp = oiio.ImageInput.open(src)
    if not inp:
        raise IOError(f"Cannot open {src}")

    spc = inp.spec()

    channel_names = get_channels(src)
    channels = []
    for chans in channel_names:
        if channel_name in chans:
            channels = chans[-1]
            break

    if channels:
        chbegin = spc.channelnames.index(channels[0])
        chend = spc.channelnames.index(channels[-1]) + 1

    pixels = inp.read_image(chbegin, chend, )


class Image:
    """
    """
    def __init__(self, pth):
        pth = pathlib.Path(pth)
        self._pth = pth.as_posix()
        self._buf = oiio.ImageBuf(self._pth)

    def convert_colorspace(self):
        ...

