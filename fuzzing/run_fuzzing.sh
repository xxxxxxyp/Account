#!/bin/bash
# Script to run Atheris fuzzing tests on the Account project

set -e

echo "=== Python项目模糊测试 (使用Atheris) ==="
echo ""

# Check if atheris is installed
if ! python3 -c "import atheris" 2>/dev/null; then
    echo "错误: Atheris未安装"
    echo "请运行: pip install atheris"
    exit 1
fi

# Function to run a single fuzz target
run_fuzz_target() {
    local target=$1
    local duration=$2
    local name=$(basename $target .py)
    
    echo "----------------------------------------"
    echo "运行模糊测试: $name"
    echo "持续时间: ${duration}秒"
    echo "----------------------------------------"
    
    # Create corpus directory for this target
    mkdir -p "corpus/$name"
    
    # Run fuzzing with timeout
    timeout ${duration}s python3 "$target" \
        -atheris_runs=1000000 \
        "corpus/$name" 2>&1 | tee "logs/${name}.log" || true
    
    echo ""
    echo "完成: $name"
    echo ""
}

# Create logs directory
mkdir -p logs

# Get duration from command line or use default
DURATION=${1:-30}

echo "每个目标将运行 ${DURATION} 秒"
echo ""

# Run each fuzz target
echo "1. 测试 AccountRecord 验证功能"
run_fuzz_target "fuzz_targets/fuzz_account_record.py" $DURATION

echo "2. 测试 QueryService 查询功能"
run_fuzz_target "fuzz_targets/fuzz_query_service.py" $DURATION

echo "3. 测试 DataManager SQL查询（SQL注入测试）"
run_fuzz_target "fuzz_targets/fuzz_data_manager.py" $DURATION

echo "========================================="
echo "模糊测试完成！"
echo ""
echo "查看日志: ls -lh logs/"
echo "查看语料库: ls -lh corpus/"
echo ""
echo "如果发现崩溃，它们会被保存在相应的语料库目录中"
echo "========================================="
