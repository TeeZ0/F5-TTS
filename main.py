from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.utils.logging import configure_logging
from app.utils.paths import ensure_runtime_directories


def main() -> int:
    configure_logging()
    ensure_runtime_directories()
    app = QApplication(sys.argv)
    app.setApplicationName("F5Narrator")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
