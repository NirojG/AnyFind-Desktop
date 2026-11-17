"""AnyFind's desktop palette and widget states."""

STYLESHEET = """
QMainWindow, QDialog {
    background: #101620;
}
QWidget {
    color: #edf2f8;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QFrame#searchPanel {
    background: #192431;
    border: 1px solid #334357;
    border-radius: 16px;
}
QLabel#brand {
    color: #edf2f8;
    font-size: 22pt;
    font-weight: 700;
}
QLabel#scope, QLabel#status {
    color: #b3c2d5;
}
QLineEdit {
    background: #111a26;
    color: #f3f7fc;
    placeholder-text-color: #a1b1c5;
    border: 1px solid #41536a;
    border-radius: 8px;
    padding: 0 12px;
    selection-background-color: #315b79;
}
QLineEdit#query {
    font-size: 13pt;
}
QLineEdit:focus {
    border: 2px solid #7fe1c1;
    padding: 0 11px;
}
QPushButton {
    background: #202e3f;
    border: 1px solid #42556d;
    border-radius: 7px;
    padding: 0 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #2d4055;
}
QPushButton:pressed {
    background: #172333;
}
QPushButton:focus {
    border-color: #7fe1c1;
}
QPushButton#scanPC {
    background: #8be4c7;
    color: #102820;
    border-color: #8be4c7;
}
QPushButton#scanPC:hover {
    background: #a9f3da;
}
QPushButton#scanPC:pressed {
    background: #6ac8a9;
}
QPushButton#scanPC:focus {
    border: 2px solid #f3fff9;
}
QPushButton:disabled {
    color: #8899ad;
    background: #192431;
    border-color: #334357;
}
QComboBox, QComboBox QAbstractItemView {
    background: #192431;
    color: #edf2f8;
    selection-background-color: #244740;
    border: 1px solid #41536a;
    padding: 4px 8px;
}
QTreeWidget {
    background: #151e2a;
    alternate-background-color: #192431;
    border: 1px solid #334357;
    border-radius: 9px;
    outline: 0;
}
QTreeWidget:focus {
    border-color: #7fe1c1;
}
QTreeWidget::item {
    height: 34px;
    padding: 0 9px;
}
QTreeWidget::item:hover {
    background: #213448;
}
QTreeWidget::item:selected {
    background: #244740;
    color: #ddfff3;
}
QHeaderView {
    background: #202e3f;
}
QHeaderView::section {
    background: #202e3f;
    color: #bfcde0;
    border: 0;
    border-bottom: 1px solid #334357;
    padding: 8px 9px;
    font-weight: 600;
}
QProgressBar {
    background: #202e3f;
    border: 0;
    border-radius: 3px;
}
QProgressBar::chunk {
    background: #8be4c7;
}
"""
