# Python项目模糊测试 - 使用Atheris

本项目使用 **Atheris**（Google开发的Python模糊测试工具）对Account记账应用进行模糊测试，发现潜在的安全漏洞、边界条件错误和程序崩溃。

## 项目说明

Account是一个基于Python和PySide6的桌面记账应用。我们使用Atheris对其核心功能进行模糊测试：
- **AccountRecord验证** - 测试记录验证逻辑
- **QueryService查询** - 测试查询和排序功能
- **DataManager数据库操作** - 测试SQL查询（包括SQL注入防护）

## 目录结构

```
fuzzing/
├── fuzz_targets/              # 模糊测试目标
│   ├── fuzz_account_record.py    # AccountRecord验证测试
│   ├── fuzz_query_service.py     # QueryService功能测试
│   └── fuzz_data_manager.py      # DataManager SQL测试
├── corpus/                    # 语料库（测试输入，运行后生成）
├── crashes/                   # 发现的崩溃用例
├── logs/                      # 测试日志（运行后生成）
├── run_fuzzing.sh            # 自动化测试脚本
└── README.md                 # 本文档
```

## 什么是Atheris？

**Atheris** 是Google开发的Python模糊测试引擎，基于libFuzzer：
- 覆盖率引导的模糊测试
- 自动生成和变异测试输入
- 高效发现边界条件和异常处理问题
- 支持Python 3.6+

### 为什么选择Atheris？

1. **原生Python支持** - 专门为Python项目设计
2. **覆盖率引导** - 智能探索代码路径
3. **快速执行** - 每秒可执行数千次测试
4. **易于集成** - 只需简单包装现有函数

## 安装Atheris

```bash
pip install atheris
```

## 测试目标说明

### 1. fuzz_account_record.py

测试 `AccountRecord.validate()` 方法的鲁棒性：
```python
# 测试点:
- 随机的type字段（应该只接受"INCOME"或"EXPENDITURE"）
- 随机的amount值（正数、负数、NaN、Infinity等）
- 随机的date格式
- 边界条件和异常处理
```

**可能发现的问题：**
- 未处理的异常类型
- 类型转换错误
- 空值或None处理问题

### 2. fuzz_query_service.py

测试 `QueryService` 的查询和排序功能：
```python
# 测试点:
- query_by_date() 使用随机日期字符串
- query_by_category() 使用随机分类ID
- sort_records() 处理各种记录列表
```

**可能发现的问题：**
- 日期比较逻辑错误
- 排序时的属性访问错误
- 空列表处理问题

### 3. fuzz_data_manager.py

测试 `DataManager` 的数据库操作，重点测试SQL注入防护：
```python
# 测试点:
- query_records() 使用各种恶意输入
- SQL参数化查询是否正确实现
- 特殊字符处理（引号、分号、注释符等）
- limit/offset边界值
- order_by SQL注入尝试
```

**可能发现的问题：**
- SQL注入漏洞
- 数据库错误处理不当
- 整数溢出

## 运行模糊测试

### 快速开始

运行所有测试目标（每个30秒）：
```bash
cd fuzzing
./run_fuzzing.sh
```

### 自定义运行时间

指定每个目标的运行时间（秒）：
```bash
./run_fuzzing.sh 60    # 每个目标运行60秒
./run_fuzzing.sh 300   # 每个目标运行5分钟
```

### 单独运行某个测试

```bash
# 测试AccountRecord
python3 fuzz_targets/fuzz_account_record.py -atheris_runs=100000

# 测试QueryService  
python3 fuzz_targets/fuzz_query_service.py -atheris_runs=100000

# 测试DataManager（SQL注入测试）
python3 fuzz_targets/fuzz_data_manager.py -atheris_runs=100000
```

## 理解测试输出

Atheris运行时会显示类似以下的输出：

```
INFO: Loaded 1 modules   (234 inline 8-bit counters)
INFO: -max_len is not provided; libFuzzer will not generate inputs larger than 4096 bytes
INFO: A corpus is not provided, starting from an empty corpus
#2      INITED cov: 15 ft: 15 corp: 1/1b exec/s: 0 rss: 45Mb
#8192   pulse  cov: 32 ft: 65 corp: 12/156b lim: 156 exec/s: 4096 rss: 47Mb
#16384  pulse  cov: 35 ft: 78 corp: 18/234b lim: 234 exec/s: 5461 rss: 49Mb
```

**关键指标：**
- `cov: 32` - 代码覆盖率（已覆盖32个代码块）
- `corp: 12/156b` - 语料库大小（12个测试用例，共156字节）
- `exec/s: 5461` - 执行速度（每秒5461次）

## 分析结果

### 查看日志

```bash
ls -lh logs/
cat logs/fuzz_account_record.log
```

### 检查崩溃

如果发现崩溃，Atheris会保存触发崩溃的输入：

```bash
# 查看崩溃文件
ls -lh corpus/*/crash-*

# 复现崩溃
python3 fuzz_targets/fuzz_account_record.py corpus/fuzz_account_record/crash-xxxxx
```

### 最小化崩溃用例

Atheris可以自动将崩溃用例最小化：

```bash
python3 fuzz_targets/fuzz_account_record.py \
  -minimize_crash=1 \
  corpus/fuzz_account_record/crash-xxxxx
```

## 常见发现示例

### 1. 类型错误
```python
# 输入: amount = NaN
# 错误: TypeError: float() argument must be a string or a number
# 修复: 添加数值验证
```

### 2. 属性访问错误
```python
# 输入: date = None
# 错误: AttributeError: 'NoneType' object has no attribute 'startswith'
# 修复: 添加None检查
```

### 3. SQL注入尝试
```python
# 输入: order_by = "date; DROP TABLE records--"
# 结果: 参数化查询正确阻止了注入
# 状态: ✓ 安全
```

## 最佳实践

### 1. 长时间运行
```bash
# 运行更长时间以发现更深层的bug
./run_fuzzing.sh 3600  # 1小时
```

### 2. 使用种子语料库
为更好的代码覆盖，提供初始测试用例：
```bash
mkdir -p corpus/fuzz_account_record
echo '{"id":"001","type":"INCOME","amount":100}' > corpus/fuzz_account_record/seed1
```

### 3. 持续集成
将模糊测试集成到CI/CD：
```yaml
# .github/workflows/fuzzing.yml
- name: Run Fuzzing Tests
  run: |
    pip install atheris
    cd fuzzing
    ./run_fuzzing.sh 120
```

### 4. 使用多核
```bash
# 并行运行多个fuzzer
python3 fuzz_targets/fuzz_account_record.py &
python3 fuzz_targets/fuzz_query_service.py &
python3 fuzz_targets/fuzz_data_manager.py &
wait
```

## 性能优化

### 提高执行速度
```bash
# 使用PyPy（如果兼容）
pypy3 fuzz_targets/fuzz_account_record.py

# 限制语料库大小
python3 fuzz_targets/fuzz_account_record.py -rss_limit_mb=2048
```

### 内存限制
```bash
# 设置内存限制（防止内存泄漏）
python3 fuzz_targets/fuzz_account_record.py -rss_limit_mb=1024
```

## 安全建议

基于模糊测试，以下是安全改进建议：

### 1. 输入验证增强
```python
def validate(self) -> bool:
    # 添加更严格的类型检查
    if not isinstance(self.type, str):
        return False
    if self.type not in ("INCOME", "EXPENDITURE"):
        return False
    
    # 验证amount
    try:
        a = float(self.amount)
        if not (0 < a < 1e10):  # 添加合理范围
            return False
    except (ValueError, TypeError):
        return False
```

### 2. SQL注入防护确认
```python
# 已正确使用参数化查询
self.driver.execute(
    "SELECT * FROM records WHERE id = ?",  # ✓ 正确
    (record_id,)
)

# 避免字符串拼接
# sql = f"SELECT * FROM records WHERE id = '{record_id}'"  # ✗ 危险
```

### 3. 异常处理
```python
try:
    result = process_data(input)
except (ValueError, TypeError) as e:
    logger.error(f"Invalid input: {e}")
    return None
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

## 故障排除

### Atheris未安装
```bash
pip install --upgrade atheris
```

### 导入错误
```bash
# 确保PYTHONPATH包含src目录
export PYTHONPATH=/home/runner/work/Account/Account:$PYTHONPATH
```

### 权限问题
```bash
chmod +x run_fuzzing.sh
```

## 参考资料

- [Atheris 官方文档](https://github.com/google/atheris)
- [libFuzzer 教程](https://llvm.org/docs/LibFuzzer.html)
- [Python 模糊测试指南](https://google.github.io/oss-fuzz/getting-started/new-project-guide/python-lang/)
- [OWASP SQL注入防护](https://owasp.org/www-community/attacks/SQL_Injection)

## 测试报告模板

运行完成后，可以生成报告：

```markdown
# 模糊测试报告

## 测试概要
- 日期: 2025-01-XX
- 工具: Atheris 3.0.0
- 目标: Account记账应用
- 运行时间: 每个目标30秒

## 结果
1. AccountRecord: 执行156,234次，覆盖率85%，发现0个崩溃
2. QueryService: 执行142,567次，覆盖率78%，发现0个崩溃
3. DataManager: 执行98,456次，覆盖率92%，发现0个崩溃

## 发现的问题
- 无严重问题

## 建议
- 增加边界值测试
- 扩展SQL注入测试用例
```

## 许可证

本测试框架遵循项目主许可证。
