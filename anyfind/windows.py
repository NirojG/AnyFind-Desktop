import ctypes
import os
from pathlib import Path

DRIVE_REMOVABLE = 2
DRIVE_FIXED = 3


def local_drives() -> list[Path]:
    get_drive_type = ctypes.windll.kernel32.GetDriveTypeW
    get_drive_type.argtypes = [ctypes.c_wchar_p]
    get_drive_type.restype = ctypes.c_uint
    return [
        Path(drive)
        for drive in os.listdrives()
        if get_drive_type(drive) in (DRIVE_REMOVABLE, DRIVE_FIXED)
    ]
