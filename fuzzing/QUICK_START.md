# 快速开始 - Python项目模糊测试

## 5分钟快速开始

### 1. 安装Atheris
```bash
pip install atheris
```

### 2. 运行测试
```bash
cd fuzzing
./run_fuzzing.sh 30  # 每个目标运行30秒
```

### 3. 查看结果
```bash
# 查看测试报告
cat FUZZING_REPORT.md

# 查看边界用例测试
python3 generate_crash_cases.py
```

## 发现的主要问题

### 🔴 问题1: 接受无穷大金额
```python
# 当前行为（错误）
record = AccountRecord("id", "INCOME", float('inf'), "2025-01-01")
record.validate()  # 返回 True ❌

# 期望行为
record.validate()  # 应该返回 False ✅
```

### 🔴 问题2: 接受NaN金额
```python
# 当前行为（错误）
record = AccountRecord("id", "INCOME", float('nan'), "2025-01-01")
record.validate()  # 返回 True ❌

# 期望行为
record.validate()  # 应该返回 False ✅
```

### 🔴 问题3: 接受超大金额
```python
# 当前行为（可能有问题）
record = AccountRecord("id", "INCOME", 1e308, "2025-01-01")
record.validate()  # 返回 True ⚠️

# 建议添加上限
# 金额应该 < 1万亿（1e12）
```

## 快速修复

在 `src/models/account_record.py` 的 `validate()` 方法中添加：

```python
import math

def validate(self) -> bool:
    if self.type not in ("INCOME", "EXPENDITURE"):
        return False
    try:
        a = float(self.amount)
        # 🔧 添加这行
        if math.isnan(a) or math.isinf(a) or a <= 0 or a > 1e12:
            return False
    except Exception:
        return False
    if not isinstance(self.date, str) or not self.date:
        return False
    return True
```

## 文件说明

```
fuzzing/
├── README.md                      # 详细文档
├── FUZZING_REPORT.md             # 测试报告
├── QUICK_START.md                # 本文档
├── run_fuzzing.sh                # 运行脚本
├── generate_crash_cases.py       # 边界测试
└── fuzz_targets/                 # 测试目标
    ├── fuzz_account_record.py    # 记录验证测试
    ├── fuzz_query_service.py     # 查询功能测试
    └── fuzz_data_manager.py      # 数据库测试
```

## 常用命令

```bash
# 安装依赖
pip install atheris

# 运行所有测试（30秒/目标）
./run_fuzzing.sh 30

# 运行更长时间（300秒/目标）
./run_fuzzing.sh 300

# 单独运行某个测试
python3 fuzz_targets/fuzz_account_record.py -atheris_runs=1000000

# 生成和测试边界用例
python3 generate_crash_cases.py

# 查看日志
cat logs/fuzz_account_record.log
```

## 测试结果摘要

| 项目 | 状态 | 说明 |
|------|------|------|
| 程序崩溃 | ✅ 0个 | 没有发现崩溃 |
| SQL注入 | ✅ 安全 | 参数化查询工作正常 |
| 输入验证 | ⚠️ 3个问题 | inf/nan/超大金额 |
| 空值处理 | ✅ 正确 | 正确拒绝None和空值 |

## 下一步

1. ✅ 阅读 `FUZZING_REPORT.md` 了解详细信息
2. 🔧 修复发现的3个验证问题
3. 🧪 运行更长时间的测试（例如1小时）
4. 📊 集成到CI/CD流程

## 帮助

遇到问题？查看：
- `README.md` - 完整文档
- `FUZZING_REPORT.md` - 测试报告
- [Atheris文档](https://github.com/google/atheris)
