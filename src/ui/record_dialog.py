"""
RecordDialog: a minimal dialog to add a new record.

Fields:
- type (EXPENDITURE / INCOME)
- amount
- date
- category (dropdown)
- remark
"""
from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QDateEdit, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt
from core.coordinator import Coordinator
from models.account_record import AccountRecord
from utils.id_gen import generate_id
from datetime import datetime


class RecordDialog(QDialog):
    def __init__(self, coordinator: Coordinator, parent=None):
        super().__init__(parent)
        self.coord = coordinator
        self.setWindowTitle("新增记录")
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        form = QFormLayout()
        # type
        self.type_cb = QComboBox()
        self.type_cb.addItems(["EXPENDITURE", "INCOME"])
        form.addRow("类型", self.type_cb)
        # amount
        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(10_000_000)
        self.amount.setDecimals(2)
        form.addRow("金额", self.amount)
        # date
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(datetime.utcnow().date())
        form.addRow("日期", self.date)
        # category
        self.cat_cb = QComboBox()
        self._load_categories()
        form.addRow("分类", self.cat_cb)
        # remark
        self.remark = QLineEdit()
        form.addRow("备注", self.remark)
        # buttons
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        form.addRow(btn_save, btn_cancel)
        self.setLayout(form)

    def _load_categories(self):
        self.cat_cb.clear()
        cats = self.coord.get_categories()
        # add a blank/none option
        self.cat_cb.addItem("(无分类)", None)
        for c in cats:
            label = f"{c.name} ({'收' if c.type == 'INCOME' else '支'})"
            self.cat_cb.addItem(label, c.id)

    def _on_save(self):
        # gather inputs
        rtype = self.type_cb.currentText()
        amount = float(self.amount.value())
        qdate = self.date.date()
        # QDate -> ISO string
        try:
            pydate = qdate.toPython()  # PySide6 convenience
            date_iso = pydate.isoformat()
        except Exception:
            # fallback
            date_iso = datetime(qdate.year(), qdate.month(), qdate.day()).isoformat()
        cat_id = self.cat_cb.currentData()
        remark = self.remark.text().strip() or None
        rec = AccountRecord(
            id=generate_id("rec"),
            type=rtype,
            amount=amount,
            date=date_iso,
            category_id=cat_id,
            remark=remark,
        )
        ok, msg = self.coord.create_record(rec)
        if ok:
            QMessageBox.information(self, "保存成功", "记录已保存。")
            self.accept()
        else:
            QMessageBox.warning(self, "保存失败", f"无法保存记录：{msg}")