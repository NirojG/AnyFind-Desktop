import re
import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QStorageInfo

from .windows import local_drives


@dataclass(frozen=True, slots=True)
class Storage:
    roots: tuple[Path, ...]
    boundaries: frozenset[Path] = frozenset()


def local_storage() -> Storage:
    if sys.platform == "win32":
        return Storage(tuple(local_drives()))
    if sys.platform == "linux":
        return linux_storage(Path("/proc/self/mountinfo").read_text(errors="surrogateescape"))

    roots = {Path("/")}
    boundaries = {Path("/System/Volumes")}
    for volume in QStorageInfo.mountedVolumes():
        path = Path(volume.rootPath())
        boundaries.add(path)
        if (
            volume.isReady()
            and bytes(volume.device()).startswith(b"/dev/")
            and not path.is_relative_to("/System/Volumes")
        ):
            roots.add(path)
    return Storage(tuple(sorted(roots)), frozenset(boundaries))


def linux_storage(mountinfo: str) -> Storage:
    roots = {Path("/")}
    boundaries = set()
    for line in mountinfo.splitlines():
        mount, filesystem = line.split(" - ", maxsplit=1)
        mount_point = mount.split()[4]
        path = Path(re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), mount_point))
        kind, source, _ = filesystem.split(maxsplit=2)
        boundaries.add(path)
        if kind != "squashfs" and (source.startswith("/dev/") or kind in {"zfs", "bcachefs"}):
            roots.add(path)
    return Storage(tuple(sorted(roots)), frozenset(boundaries))
