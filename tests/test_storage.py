import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from anyfind.storage import linux_storage, local_storage


class LinuxStorageTests(unittest.TestCase):
    def test_selects_local_roots_and_treats_other_mounts_as_boundaries(self):
        mount_info = r"""
31 1 8:1 / / rw - ext4 /dev/sda1 rw
32 31 8:2 / /media/External\040Drive rw - exfat /dev/sdb1 rw
33 31 0:5 / /proc rw - proc proc rw
34 31 0:6 / /mnt/share rw - nfs server:/share rw
35 31 7:0 / /snap/tool ro - squashfs /dev/loop0 ro
36 31 0:7 / /home rw - zfs pool/home rw
""".strip()
        storage = linux_storage(mount_info)
        self.assertEqual(set(storage.roots), {Path("/"), Path("/media/External Drive"), Path("/home")})
        self.assertTrue(
            {Path("/proc"), Path("/mnt/share"), Path("/snap/tool")}.issubset(storage.boundaries)
        )


class MacStorageTests(unittest.TestCase):
    def test_keeps_external_volumes_and_excludes_system_aliases_and_network_shares(self):
        def volume(path, device):
            return Mock(
                rootPath=Mock(return_value=path),
                device=Mock(return_value=device),
                isReady=Mock(return_value=True),
            )

        volumes = [
            volume("/", b"/dev/disk1s1"),
            volume("/System/Volumes/Data", b"/dev/disk1s2"),
            volume("/Volumes/Archive", b"/dev/disk2s1"),
            volume("/Volumes/Team", b"//server/Team"),
        ]
        with patch("anyfind.storage.sys.platform", "darwin"):
            with patch("anyfind.storage.QStorageInfo.mountedVolumes", return_value=volumes):
                storage = local_storage()

        self.assertEqual(set(storage.roots), {Path("/"), Path("/Volumes/Archive")})
        self.assertIn(Path("/System/Volumes"), storage.boundaries)
        self.assertIn(Path("/Volumes/Team"), storage.boundaries)
