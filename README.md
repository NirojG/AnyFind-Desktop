# AnyFind

AnyFind is a desktop app for finding files and folders by name or extension. It runs offline and gives exact filename matches priority over partial matches. The source supports Windows, macOS, and desktop Linux. The desktop app has been smoke-tested on Windows.

![AnyFind searching two drives for PDF contracts using sample data](docs/anyfind-search.png)

AnyFind starts in light mode. Use **Dark mode** to switch themes. The app remembers your selection. [See the dark theme](docs/anyfind-dark-mode.png).

## Run from source

Use Python 3.12 or later. On Windows, run these commands from the project directory in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m anyfind
```

On macOS or desktop Linux, run:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m anyfind
```

## Build a desktop bundle

Install PyInstaller in the same virtual environment and run the build on the target operating system. Activate the environment first, or replace `python` with its full path.

```sh
python -m pip install pyinstaller
python -m PyInstaller AnyFind.spec
```

Look for `AnyFind.app` under `dist` on macOS or the executable inside `dist/AnyFind` on Windows and Linux. Keep the entire bundle together when moving it. The Windows x64 bundle was built and verified to open and close cleanly on Windows 11. Native macOS and Linux bundles still need build and launch verification.

## Search

- **Scan this PC** searches available fixed and removable local drives with drive letters on Windows. **Scan this computer** searches the startup filesystem and detected local volumes on macOS and Linux.
- **Choose drive** searches one local drive. **Choose folder** searches one folder and its descendants.
- Type a filename, part of a name, or a folder name. Enter an extension such as `pdf` or `.pdf` to narrow the results.
- Double-click a result to open it, or select it and click **Open containing folder** to open its parent in the system file manager.

AnyFind reads file and folder metadata after you choose a scope. The first search waits for the scan to finish. Typing reuses the in-memory snapshot, and rescanning the selected scope picks up changes on disk. Access depends on your account and the operating system's privacy settings. AnyFind reports read errors and skips symbolic links and Windows reparse points, including junctions. On macOS and Linux, detected mount boundaries keep network and virtual filesystems out of the whole-computer scan. A folder explicitly selected within one of those filesystems can still be searched.

## Implementation and verification

The PySide6 window delegates scanning and searching to a single background worker. The scanner uses `os.scandir` to collect metadata. Search ranks full names, names without extensions, prefixes, and substrings in that order, with case-insensitive comparisons. It counts all matches and keeps only the best 250 for display.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The desktop smoke check used temporary directories to exercise all three scope controls, multi-root search, metadata, empty and error states, and the paths passed to Windows for open actions. Whole-PC scan duration and memory use depend on the number of entries and the storage device. Full-drive performance has yet to be benchmarked.

## Roadmap

1. **Working desktop search** — whole-PC, drive, and folder scans, live filename and extension filtering, metadata, and open actions.
2. **Persistent local indexing** — save metadata to SQLite, update it incrementally, support exclusions, and show scan progress while keeping search available.
3. **Smarter search** — rank typo-tolerant matches and path or type clues, then evaluate local document text extraction and multilingual terms for description-based queries.
4. **File interaction** — reveal a file in Explorer, copy paths and names, preview supported formats, sort, add keyboard shortcuts, and keep recent searches.
5. **Reliability and packaging** — benchmark large directories, test indexing and shutdown, and verify desktop bundles on Windows, macOS, and Linux.
