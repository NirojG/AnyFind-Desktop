import heapq
import os
import stat
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from threading import Event


@dataclass(frozen=True, slots=True)
class Entry:
    path: Path
    is_folder: bool
    size: int
    modified: float

    @property
    def extension(self):
        return "" if self.is_folder else self.path.suffix


@dataclass(slots=True)
class Scan:
    entries: list[Entry]
    skipped: int


@dataclass(slots=True)
class Matches:
    entries: list[Entry]
    total: int


def scan_folders(
    roots: list[Path] | tuple[Path, ...],
    cancelled: Event,
    boundaries: frozenset[Path] = frozenset(),
) -> Scan:
    if not roots:
        raise OSError("No local drives were found.")
    pending = list(reversed(roots))
    root_paths = set(roots)
    opened_roots = 0
    last_error = None
    entries = []
    skipped = 0
    while pending and not cancelled.is_set():
        folder = pending.pop()
        try:
            with os.scandir(folder) as children:
                if folder in root_paths:
                    opened_roots += 1
                for child in children:
                    if cancelled.is_set():
                        break
                    path = Path(child.path)
                    if path in boundaries:
                        continue
                    try:
                        metadata = child.stat(follow_symlinks=False)
                    except OSError:
                        skipped += 1
                        continue
                    # Skip junctions and other reparse points that could leave the chosen scope.
                    if stat.S_ISLNK(metadata.st_mode) or (
                        getattr(metadata, "st_file_attributes", 0)
                        & stat.FILE_ATTRIBUTE_REPARSE_POINT
                    ):
                        continue
                    is_folder = stat.S_ISDIR(metadata.st_mode)
                    if is_folder:
                        pending.append(path)
                    entries.append(Entry(path, is_folder, metadata.st_size, metadata.st_mtime))
        except OSError as error:
            last_error = error
            skipped += 1
    if not opened_roots and last_error is not None and not cancelled.is_set():
        raise last_error
    return Scan(entries, skipped)


def search(
    entries: Iterable[Entry], query: str, extension: str, cancelled: Event, limit: int = 250
) -> Matches:
    query = query.strip().casefold()
    extension = extension.strip().casefold().removeprefix(".")
    total = 0

    def candidates():
        nonlocal total
        for entry in entries:
            if cancelled.is_set():
                break
            suffix = entry.extension.casefold()
            if extension and suffix.removeprefix(".") != extension:
                continue
            name = entry.path.name.casefold()
            if not query or name == query:
                priority = 0
            elif not entry.is_folder and name.removesuffix(suffix) == query:
                priority = 1
            elif name.startswith(query):
                priority = 2
            elif query in name:
                priority = 3
            else:
                continue
            total += 1
            yield priority, name, str(entry.path).casefold(), entry

    best = heapq.nsmallest(limit, candidates(), key=lambda match: match[:3])
    return Matches([match[3] for match in best], total)
