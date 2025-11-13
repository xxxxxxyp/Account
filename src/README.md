# 记账程序 - Python 桌面（精简版）

说明：
- 这是一个简化的桌面记账应用骨架，采用 PySide6 和 sqlite3。
- 目录结构：models / data / services / core / ui / db

快速运行（开发时）：
1. 创建虚拟环境并安装依赖：
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. 初始化数据库（执行 db/schema.sql）：
   python -c "import sqlite3; print('Run schema manually or implement migration')"

3. 启动应用：
   python src/main.py

后续建议：
- 实现 DataManager 的迁移/备份/导入逻辑
- 用 matplotlib 或 pyqtgraph 绘制统计图表
- 增加单元测试（pytest）