"""
统计视图骨架：从 coordinator 获取统计并渲染（可用 matplotlib/pyqtgraph）
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from core.coordinator import Coordinator

class StatsView(QWidget):
    def __init__(self, coordinator: Coordinator, parent=None):
        super().__init__(parent)
        self.coord = coordinator
        self.setWindowTitle("统计")
        self._init_ui()

    def _init_ui(self):
        v = QVBoxLayout()
        summary = self.coord.get_statistics_summary()
        v.addWidget(QLabel(f"总计: {summary['total_by_type']}"))
        # TODO: 用图表库绘制饼图/时间序列
        self.setLayout(v)