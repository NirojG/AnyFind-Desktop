import tempfile
import unittest
from pathlib import Path
from threading import Event

from anyfind.search import scan_folders, search


class SearchTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.cancelled = Event()
        (self.root / "Contracts").mkdir()
        (self.root / "Archive").mkdir()
        for name in (
            "Contracts/Contract.PDF",
            "Contracts/Contract-final.pdf",
            "Archive/employment-contract.pdf",
            "contract-notes.txt",
        ):
            (self.root / name).write_bytes(b"sample")
        self.scan = scan_folders([self.root], self.cancelled)

    def test_exact_full_name_comes_before_partial_matches(self):
        matches = search(self.scan.entries, "contract.pdf", "", self.cancelled)
        self.assertEqual(
            [entry.path.name for entry in matches.entries],
            ["Contract.PDF", "employment-contract.pdf"],
        )

    def test_combines_case_insensitive_filename_and_extension_and_limits_rows(self):
        matches = search(self.scan.entries, " CONTRACT ", " .PDF ", self.cancelled, limit=2)
        self.assertEqual(matches.total, 3)
        self.assertEqual(
            [entry.path.name for entry in matches.entries], ["Contract.PDF", "Contract-final.pdf"]
        )
        self.assertEqual(matches.entries[0].size, 6)
        self.assertEqual(matches.entries[0].path.parent, self.root / "Contracts")

    def test_matches_folders_and_empty_query_filters_by_extension(self):
        folders = search(self.scan.entries, "arch", "", self.cancelled)
        self.assertTrue(folders.entries[0].is_folder)
        self.assertEqual(folders.entries[0].path.name, "Archive")
        self.assertEqual(search(self.scan.entries, "", "pdf", self.cancelled).total, 3)
        self.assertEqual(search(self.scan.entries, "", "zip", self.cancelled).total, 0)

    def test_scans_multiple_roots_and_reports_an_unavailable_root(self):
        roots = [self.root / name for name in ("Contracts", "Missing", "Archive")]
        scan = scan_folders(roots, self.cancelled)
        self.assertEqual(len(scan.entries), 3)
        self.assertEqual(scan.skipped, 1)

    def test_raises_when_no_root_can_be_opened(self):
        with self.assertRaises(FileNotFoundError):
            scan_folders([self.root / "Missing"], self.cancelled)

    def test_mounted_volume_is_scanned_only_when_included_as_a_root(self):
        mount = self.root / "Archive"
        boundaries = frozenset({mount})
        single = scan_folders([self.root], self.cancelled, boundaries)
        combined = scan_folders([self.root, mount], self.cancelled, boundaries)
        self.assertFalse(any(entry.path.is_relative_to(mount) for entry in single.entries))
        self.assertEqual(
            [entry.path.name for entry in combined.entries if entry.path.is_relative_to(mount)],
            ["employment-contract.pdf"],
        )

    def test_cancelled_work_stops_before_scanning_or_matching(self):
        self.cancelled.set()
        self.assertEqual(scan_folders([self.root], self.cancelled).entries, [])
        self.assertEqual(search(self.scan.entries, "", "", self.cancelled).total, 0)
