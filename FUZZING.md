# 模糊测试文档

本项目已集成 **Atheris** 模糊测试框架，用于发现潜在的安全漏洞和边界条件错误。

## 什么是模糊测试？

模糊测试（Fuzzing）是一种自动化测试技术，通过向程序输入大量随机、异常或边界数据，来发现潜在的崩溃、内存泄漏、安全漏洞等问题。

## 为什么使用Atheris？

由于本项目是Python编写的，我们选择了Google开发的 **Atheris** 而不是传统的AFL++：

- ✅ **原生Python支持** - 无需编译，直接测试Python代码
- ✅ **覆盖率引导** - 智能探索代码路径，提高测试效率
- ✅ **工业级工具** - Google用于OSS-Fuzz项目的生产工具
- ✅ **高执行速度** - 每秒可执行数千至数万次测试

相比之下，AFL++主要用于C/C++项目，不适合本项目。

## 快速开始

```bash
# 1. 安装Atheris
pip install atheris

# 2. 进入fuzzing目录
cd fuzzing

# 3. 运行测试（每个目标30秒）
./run_fuzzing.sh 30

# 4. 查看结果
cat FUZZING_REPORT.md
```

## 测试覆盖范围

### 1. AccountRecord验证测试
- 文件: `fuzzing/fuzz_targets/fuzz_account_record.py`
- 测试: 记录验证逻辑，包括类型、金额、日期检查
- 发现: 3个输入验证问题

### 2. QueryService功能测试
- 文件: `fuzzing/fuzz_targets/fuzz_query_service.py`
- 测试: 查询和排序功能
- 结果: 运行正常，无问题

### 3. DataManager SQL测试
- 文件: `fuzzing/fuzz_targets/fuzz_data_manager.py`
- 测试: SQL查询操作，重点测试SQL注入防护
- 结果: SQL注入防护有效

## 发现的问题

通过模糊测试，我们发现了以下问题：

### 🔴 问题1: 接受无穷大金额
```python
record = AccountRecord("id", "INCOME", float('inf'), "2025-01-01")
record.validate()  # 返回 True （应该是 False）
```

### 🔴 问题2: 接受NaN金额
```python
record = AccountRecord("id", "INCOME", float('nan'), "2025-01-01")
record.validate()  # 返回 True （应该是 False）
```

### 🔴 问题3: 接受超大金额
```python
record = AccountRecord("id", "INCOME", 1e308, "2025-01-01")
record.validate()  # 返回 True （应考虑添加上限）
```

## 测试统计

- **总执行次数**: ~2,000,000次
- **测试时长**: 约2分钟
- **发现崩溃**: 0个
- **发现问题**: 3个输入验证问题
- **SQL注入测试**: ✅ 通过

## 文档结构

```
fuzzing/
├── README.md              # 完整使用文档
├── FUZZING_REPORT.md     # 详细测试报告
├── QUICK_START.md        # 5分钟快速指南
├── run_fuzzing.sh        # 自动化测试脚本
├── generate_crash_cases.py  # 边界用例生成器
└── fuzz_targets/         # 测试目标文件
```

## 下一步行动

1. 📖 阅读 [`fuzzing/QUICK_START.md`](fuzzing/QUICK_START.md) - 5分钟快速指南
2. 📊 查看 [`fuzzing/FUZZING_REPORT.md`](fuzzing/FUZZING_REPORT.md) - 详细测试报告
3. 🔧 修复发现的3个验证问题
4. 🧪 定期运行模糊测试（建议集成到CI/CD）

## 运行模糊测试

### 基本用法
```bash
cd fuzzing
./run_fuzzing.sh 30  # 每个目标30秒
```

### 长时间测试
```bash
./run_fuzzing.sh 300  # 每个目标5分钟
./run_fuzzing.sh 3600 # 每个目标1小时
```

### 单独测试某个组件
```bash
python3 fuzz_targets/fuzz_account_record.py -atheris_runs=1000000
```

### 生成和测试边界用例
```bash
python3 generate_crash_cases.py
```

## 集成到CI/CD

可以将模糊测试添加到CI流程：

```yaml
# .github/workflows/fuzzing.yml
name: Fuzzing Tests

on: [push, pull_request]

jobs:
  fuzz:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r src/requirements.txt
          pip install atheris
      - name: Run fuzzing tests
        run: |
          cd fuzzing
          ./run_fuzzing.sh 60
      - name: Generate edge case tests
        run: |
          cd fuzzing
          python3 generate_crash_cases.py
```

## 相关资源

- [Atheris GitHub](https://github.com/google/atheris) - 官方仓库
- [Google OSS-Fuzz](https://github.com/google/oss-fuzz) - 开源模糊测试服务
- [模糊测试最佳实践](https://google.github.io/oss-fuzz/) - Google文档

## 问题反馈

如果在运行模糊测试时遇到问题，请：

1. 查看 `fuzzing/README.md` 中的故障排除部分
2. 检查 `fuzzing/logs/` 目录中的日志文件
3. 确保已安装所有依赖：`pip install -r src/requirements.txt`

---

**注意**: 模糊测试是持续的安全实践。建议定期运行测试，特别是在添加新功能或修改验证逻辑后。
