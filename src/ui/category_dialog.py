"""
管理分类的对话框骨架（增删改）
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton
from core.coordinator import Coordinator

class CategoryDialog(QDialog):
    def __init__(self, coordinator: Coordinator, parent=None):
        super().__init__(parent)
        self.coord = coordinator
        self.setWindowTitle("分类管理")
        self._init_ui()

    def _init_ui(self):
        v = QVBoxLayout()
        self.list_widget = QListWidget()
        self._reload()
        v.addWidget(self.list_widget)
        # TODO: add/add/edit/delete buttons
        self.setLayout(v)

    def _reload(self):
        self.list_widget.clear()
        for c in self.coord.get_categories():
            self.list_widget.addItem(f"{c.name} ({c.type})")