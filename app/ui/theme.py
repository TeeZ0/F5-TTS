from __future__ import annotations

DARK_THEME = """
QWidget {
    background-color: #121417;
    color: #f2f4f8;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 10.5pt;
}
QGroupBox {
    border: 1px solid #2d333b;
    border-radius: 10px;
    margin-top: 12px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background-color: #1b1f24;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px;
    selection-background-color: #2f81f7;
}
QPushButton {
    background-color: #238636;
    border: 0;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    min-height: 32px;
    padding: 7px 14px;
}
QPushButton:hover {
    background-color: #2ea043;
}
QPushButton:disabled {
    background-color: #30363d;
    color: #8b949e;
}
QPushButton#secondaryButton {
    background-color: #30363d;
}
QPushButton#secondaryButton:hover {
    background-color: #3d444d;
}
QProgressBar {
    background-color: #1b1f24;
    border: 1px solid #30363d;
    border-radius: 8px;
    height: 18px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #2f81f7;
    border-radius: 8px;
}
QSlider::groove:horizontal {
    background-color: #30363d;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background-color: #2f81f7;
    border-radius: 8px;
    margin: -5px 0;
    width: 16px;
}
"""
