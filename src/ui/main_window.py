"""
MainWindow: minimal app window containing controls to add a record and view recent records.
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from core.coordinator import Coordinator
from ui.record_dialog import RecordDialog


class MainWindow(QMainWindow):
    def __init__(self, coordinator: Coordinator):
        super().__init__()
        self.coord = coordinator
        self.setWindowTitle("记账程序 - 最小界面")
        self._init_ui()
        # show initial data
        self.refresh_records()

    def _init_ui(self):
        central = QWidget()
        v = QVBoxLayout()
        h = QHBoxLayout()
        btn_add = QPushButton("新增记录")
        btn_add.clicked.connect(self.open_add_dialog)
        btn_refresh = QPushButton("刷新列表")
        btn_refresh.clicked.connect(self.refresh_records)
        h.addWidget(btn_add)
        h.addWidget(btn_refresh)
        v.addLayout(h)
        # table for recent records
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["类型", "金额", "日期", "分类", "备注"])
        v.addWidget(self.table)
        central.setLayout(v)
        self.setCentralWidget(central)

    def open_add_dialog(self):
        dlg = RecordDialog(self.coord, parent=self)
        if dlg.exec():
            # if dialog accepted, refresh list
            self.refresh_records()

    def refresh_records(self):
        records = self.coord.list_recent_records(limit=100)
        self.table.setRowCount(0)
        for r in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r.type))
            self.table.setItem(row, 1, QTableWidgetItem(f"{float(r.amount):.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(r.date))
            # look up category name (may be None)
            cat_name = ""
            if r.category_id:
                cat = self.coord.dm.get_category(r.category_id)
                if cat:
                    cat_name = cat.name
            self.table.setItem(row, 3, QTableWidgetItem(cat_name))
            self.table.setItem(row, 4, QTableWidgetItem(r.remark or ""))