from ctypes import *
from sys import platform
import os

_os_clib_map = {
    "win32": "\\clib\\howmonochromatic.dll",
    "linux": "/clib/libhowmonochromatic.so"
}

_clib_path = os.path.dirname(__file__) + _os_clib_map.get(platform, "")

_clib = CDLL(_clib_path)

_clib.howMono.restype = c_double


class Analyser:
    def __init__(self):
        self._clib = _clib

    def __enter__(self):
        self._clib.hs_init(0, 0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clib.hs_exit()

    def how_mono(self, g):
        return self._clib.howMono(g.encode())
