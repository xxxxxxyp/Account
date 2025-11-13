#!/usr/bin/env python3
"""
Entry point: start the Qt application.
Run: python src/main.py
"""
import sys
from PySide6.QtWidgets import QApplication
from app import create_app

def main():
    app = QApplication(sys.argv)
    container = create_app()
    window = container["main_window"]
    window.resize(800, 600)
    window.show()
    try:
        app.exec()
    finally:
        # close DB connection gracefully
        container["data_manager"].close()

if __name__ == "__main__":
    main()