from __future__ import annotations

from datetime import datetime
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor
from PySide6.QtWidgets import QPlainTextEdit
from enum import Enum

BASE_MAX_LINE = 128

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    CMD = "CMD"

class Colour(Enum):
    WHITE = 0
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4

class LogWidget(QPlainTextEdit):
    """
    Console log widget for displaying any application output and messages.
    """

    def __init__(self, style_settings: str, max_lines: int = BASE_MAX_LINE) -> None:
        super().__init__()

        # Have a limit to number of lines that you can see
        # Otherwise application may lag
        self._max_lines = max_lines
        self._current_lines = 0
        self._lines = []
        
        self.setMaximumHeight(720)
        self.setMinimumHeight(720)
        
        self.setStyleSheet(style_settings)
        
        self.setPlainText("")
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self._colour_map = {
            Colour.WHITE: (255, 255, 255),
            Colour.RED: (255, 0, 0),
            Colour.YELLOW: (255, 255, 0),
            Colour.GREEN: (0, 128, 0),
            Colour.BLUE: (0, 0, 255)
        }

    # Add a new line of text to the log widget externally
    @Slot(str)
    def addLine(self, log_level: LogLevel, message: str, colour: Colour = Colour.WHITE) -> None:
        """Add a new line with timestamp and message with max line number limits"""
        
        # Get current time for timestamp with log entry formatting
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {log_level} - {message}\n"

        self._lines.append(log_entry)

        if self._current_lines > self._max_lines:
            self._lines.pop(0)
        
        new_text = "".join(self._lines)
        
        # Once new text is set, scroll to the bottom
        self.setPlainText(new_text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())