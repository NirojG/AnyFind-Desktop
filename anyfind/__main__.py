import sys

from PySide6.QtWidgets import QApplication

from .window import SearchWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AnyFind")
    window = SearchWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
