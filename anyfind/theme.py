"""Shared desktop widget styles and light/dark color palettes."""

from string import Template

_PALETTE = {
    "canvas": ("#101620", "#f2f5f8"),
    "text": ("#edf2f8", "#142332"),
    "panel": ("#192431", "#ffffff"),
    "outline": ("#334357", "#c6d1dc"),
    "muted": ("#b3c2d5", "#43556a"),
    "input": ("#111a26", "#f7f9fb"),
    "input_text": ("#f3f7fc", "#142332"),
    "placeholder": ("#a1b1c5", "#52667c"),
    "input_outline": ("#41536a", "#9dafc0"),
    "text_selection": ("#315b79", "#b9e6da"),
    "focus": ("#7fe1c1", "#157b65"),
    "control": ("#202e3f", "#eaf0f4"),
    "control_outline": ("#42556d", "#9eafbf"),
    "control_hover": ("#2d4055", "#dbe7ef"),
    "control_pressed": ("#172333", "#cddce7"),
    "primary": ("#8be4c7", "#126450"),
    "primary_text": ("#102820", "#ffffff"),
    "primary_hover": ("#a9f3da", "#18745e"),
    "primary_pressed": ("#6ac8a9", "#0c5140"),
    "primary_focus": ("#f3fff9", "#183d34"),
    "disabled": ("#8899ad", "#607185"),
    "selected": ("#244740", "#cbeee3"),
    "selected_text": ("#ddfff3", "#103b30"),
    "table": ("#151e2a", "#ffffff"),
    "alternate_row": ("#192431", "#f5f8fa"),
    "hover_row": ("#213448", "#e6f1f5"),
    "header_text": ("#bfcde0", "#384e62"),
}

_STYLESHEET = Template("""
QMainWindow, QDialog {
    background: $canvas;
}
QWidget {
    color: $text;
    font-size: 10pt;
}
QFrame#searchPanel {
    background: $panel;
    border: 1px solid $outline;
    border-radius: 16px;
}
QLabel#brand {
    color: $text;
    font-size: 22pt;
    font-weight: 700;
}
QLabel#scope, QLabel#status {
    color: $muted;
}
QLineEdit {
    background: $input;
    color: $input_text;
    placeholder-text-color: $placeholder;
    border: 1px solid $input_outline;
    border-radius: 8px;
    padding: 0 12px;
    selection-background-color: $text_selection;
}
QLineEdit#query {
    font-size: 13pt;
}
QLineEdit:focus {
    border: 2px solid $focus;
    padding: 0 11px;
}
QPushButton {
    background: $control;
    border: 1px solid $control_outline;
    border-radius: 7px;
    padding: 0 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: $control_hover;
}
QPushButton:pressed {
    background: $control_pressed;
}
QPushButton:focus {
    border-color: $focus;
}
QPushButton#scanPC {
    background: $primary;
    color: $primary_text;
    border-color: $primary;
}
QPushButton#scanPC:hover {
    background: $primary_hover;
}
QPushButton#scanPC:pressed {
    background: $primary_pressed;
}
QPushButton#scanPC:focus {
    border: 2px solid $primary_focus;
}
QPushButton:disabled {
    color: $disabled;
    background: $panel;
    border-color: $outline;
}
QComboBox, QComboBox QAbstractItemView {
    background: $panel;
    color: $text;
    selection-background-color: $selected;
    border: 1px solid $input_outline;
    padding: 4px 8px;
}
QTreeWidget {
    background: $table;
    alternate-background-color: $alternate_row;
    border: 1px solid $outline;
    border-radius: 9px;
    outline: 0;
}
QTreeWidget:focus {
    border-color: $focus;
}
QTreeWidget::item {
    height: 34px;
    padding: 0 9px;
}
QTreeWidget::item:hover {
    background: $hover_row;
}
QTreeWidget::item:selected {
    background: $selected;
    color: $selected_text;
}
QHeaderView {
    background: $control;
}
QHeaderView::section {
    background: $control;
    color: $header_text;
    border: 0;
    border-bottom: 1px solid $outline;
    padding: 8px 9px;
    font-weight: 600;
}
QProgressBar {
    background: $control;
    border: 0;
    border-radius: 3px;
}
QProgressBar::chunk {
    background: $primary;
}
""")


def stylesheet(dark: bool) -> str:
    colors = {
        name: dark_color if dark else light_color
        for name, (dark_color, light_color) in _PALETTE.items()
    }
    return _STYLESHEET.substitute(colors)
