import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

from PySide6.QtCore import QDateTime, QTimer, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .search import Matches, scan_folders, search
from .theme import STYLESHEET
from .windows import local_drives

ENTRY_ROLE = Qt.ItemDataRole.UserRole


class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnyFind")
        self.resize(1040, 600)
        self.setMinimumSize(780, 440)
        self.setStyleSheet(STYLESHEET)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="anyfind")
        self._future = None
        self._cancelled = Event()
        self._scan = None
        self._scanning = False
        self._poll = QTimer(self, interval=30)
        self._poll.timeout.connect(self._check_work)
        self._debounce = QTimer(self, interval=100, singleShot=True)
        self._debounce.timeout.connect(self._start_search)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)
        self.setCentralWidget(container)

        search_panel = QFrame()
        search_panel.setObjectName("searchPanel")
        panel_layout = QVBoxLayout(search_panel)
        panel_layout.setContentsMargins(20, 15, 20, 18)
        panel_layout.setSpacing(12)
        layout.addWidget(search_panel)

        heading = QLabel("AnyFind")
        heading.setObjectName("brand")
        panel_layout.addWidget(heading)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        self.query = QLineEdit(placeholderText="Search files and folders", clearButtonEnabled=True)
        self.query.setObjectName("query")
        self.query.setAccessibleName("Search files and folders")
        self.query.setMinimumHeight(48)
        self.extension = QLineEdit(placeholderText="Extension, e.g. pdf", clearButtonEnabled=True)
        self.extension.setAccessibleName("File extension filter")
        self.extension.setMinimumHeight(48)
        self.extension.setFixedWidth(174)
        search_row.addWidget(self.query, 1)
        search_row.addWidget(self.extension)
        panel_layout.addLayout(search_row)

        scope_row = QHBoxLayout()
        scope_row.setSpacing(8)
        scan_pc = QPushButton("Scan this PC")
        scan_pc.setObjectName("scanPC")
        scan_pc.clicked.connect(self._scan_pc)
        choose_drive = QPushButton("Choose drive…")
        choose_drive.clicked.connect(self._choose_drive)
        choose_folder = QPushButton("Choose folder…")
        choose_folder.clicked.connect(self._choose_folder)
        for button in (scan_pc, choose_drive, choose_folder):
            button.setMinimumHeight(34)
            scope_row.addWidget(button)
        self.scope = QLabel()
        self.scope.setObjectName("scope")
        self.scope.setContentsMargins(8, 0, 0, 0)
        self.scope.setTextFormat(Qt.TextFormat.PlainText)
        self.scope.setWordWrap(True)
        scope_row.addWidget(self.scope, 1)
        panel_layout.addLayout(scope_row)

        self.results = QTreeWidget()
        self.results.setHeaderLabels(["Name", "Location", "Type / extension", "Size", "Modified"])
        self.results.setRootIsDecorated(False)
        self.results.setAlternatingRowColors(True)
        self.results.setUniformRowHeights(True)
        header = self.results.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column, width in ((0, 238), (2, 125), (3, 98), (4, 154)):
            self.results.setColumnWidth(column, width)
        self.results.itemActivated.connect(lambda item, _: self._open(item))
        self.results.itemSelectionChanged.connect(self._update_actions)
        layout.addWidget(self.results, 1)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        self.status = QLabel("Scan this PC or choose a location to start.")
        self.status.setObjectName("status")
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        self.progress = QProgressBar(minimum=0, maximum=0, textVisible=False)
        self.progress.setAccessibleName("Scan progress")
        self.progress.setFixedWidth(100)
        self.progress.setFixedHeight(6)
        self.progress.hide()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(lambda: self._open(self.results.currentItem()))
        self.folder_button = QPushButton("Open containing folder")
        self.folder_button.clicked.connect(
            lambda: self._open(self.results.currentItem(), containing_folder=True)
        )
        self.open_button.setMinimumHeight(34)
        self.folder_button.setMinimumHeight(34)
        footer.addWidget(self.status, 1)
        footer.addWidget(self.progress)
        footer.addWidget(self.open_button)
        footer.addWidget(self.folder_button)
        layout.addLayout(footer)

        self.query.textChanged.connect(self._queue_search)
        self.extension.textChanged.connect(self._queue_search)
        self._file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self._folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self._update_actions()
        self.query.setFocus()

    def _scan_pc(self):
        try:
            drives = local_drives()
        except OSError as error:
            QMessageBox.warning(self, "Could not list local drives", str(error))
            return
        self._start_scan(drives, "This PC · local drives")

    def _choose_drive(self):
        try:
            drives = [str(path) for path in local_drives()]
        except OSError as error:
            QMessageBox.warning(self, "Could not list local drives", str(error))
            return
        if not drives:
            QMessageBox.information(self, "AnyFind", "No local drives were found.")
            return
        drive, confirmed = QInputDialog.getItem(self, "Choose drive", "Drive", drives, editable=False)
        if confirmed:
            self._start_scan([Path(drive)], drive)

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose folder")
        if folder:
            self._start_scan([Path(folder)], folder)

    def _cancel_work(self):
        self._cancelled.set()
        if self._future is not None:
            self._future.cancel()
            self._future = None

    def _start_scan(self, roots: list[Path], label: str):
        self._debounce.stop()
        self._cancel_work()
        self._scan = None
        self._scanning = True
        self.scope.setText(label)
        self.scope.setToolTip("\n".join(map(str, roots)))
        self.results.clear()
        self.status.setText("Scanning files and folders…")
        self.progress.show()
        self._cancelled = Event()
        self._future = self._executor.submit(scan_folders, roots, self._cancelled)
        self._poll.start()
        self.query.setFocus()

    def _queue_search(self):
        if self._scan is not None:
            self._cancel_work()
            self.results.clear()
            self.status.setText("Searching…")
            self._debounce.start()

    def _start_search(self):
        self._cancelled = Event()
        self._future = self._executor.submit(
            search, self._scan.entries, self.query.text(), self.extension.text(), self._cancelled
        )
        self._poll.start()

    def _check_work(self):
        if self._future is None:
            self._poll.stop()
            return
        if not self._future.done():
            return
        self._poll.stop()
        completed, self._future = self._future, None
        was_scanning, self._scanning = self._scanning, False
        self.progress.hide()
        try:
            result = completed.result()
        except Exception as error:
            operation = "Scan" if was_scanning else "Search"
            self.status.setText(f"{operation} failed. {error}")
            return
        if was_scanning:
            self._scan = result
            self.status.setText("Searching…")
            self._start_search()
        else:
            self._show_matches(result)

    def _show_matches(self, matches: Matches):
        rows = []
        for entry in matches.entries:
            modified = QDateTime.fromMSecsSinceEpoch(int(entry.modified * 1000))
            row = QTreeWidgetItem([
                entry.path.name,
                str(entry.path.parent),
                "Folder" if entry.is_folder else entry.extension or "—",
                "—" if entry.is_folder else f"{entry.size:,} B",
                modified.toString("yyyy-MM-dd HH:mm"),
            ])
            row.setData(0, ENTRY_ROLE, str(entry.path))
            row.setIcon(0, self._folder_icon if entry.is_folder else self._file_icon)
            row.setToolTip(0, str(entry.path))
            row.setToolTip(1, str(entry.path.parent))
            row.setTextAlignment(3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            rows.append(row)
        self.results.addTopLevelItems(rows)
        status = f"{matches.total:,} results" if matches.total else "No matching files or folders."
        if matches.total > len(rows):
            status = f"Showing {len(rows):,} of {matches.total:,} results. Refine your search for more."
        if self._scan.skipped:
            status += f"  {self._scan.skipped:,} locations or items could not be read."
        self.status.setText(status)

    def _update_actions(self):
        selected = bool(self.results.selectedItems())
        self.open_button.setEnabled(selected)
        self.folder_button.setEnabled(selected)

    def _open(self, item, containing_folder=False):
        if item is None:
            return
        path = Path(item.data(0, ENTRY_ROLE))
        target = path.parent if containing_folder else path
        try:
            os.startfile(str(target))
        except OSError as error:
            QMessageBox.warning(self, "Could not open location", str(error))

    def closeEvent(self, event):
        self._debounce.stop()
        self._poll.stop()
        self._cancel_work()
        self._executor.shutdown(wait=False, cancel_futures=True)
        super().closeEvent(event)
