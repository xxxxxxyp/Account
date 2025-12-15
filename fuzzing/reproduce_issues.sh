#!/bin/bash
# Script to reproduce discovered issues

echo "=========================================="
echo "Account项目模糊测试 - 问题复现脚本"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo "本脚本将复现通过模糊测试发现的问题"
echo ""
echo "按Enter继续..."
read

echo "----------------------------------------"
echo "运行边界用例测试..."
echo "----------------------------------------"
python3 generate_crash_cases.py

echo ""
echo "----------------------------------------"
echo "总结"
echo "----------------------------------------"
echo ""
echo "✅ 发现了3个输入验证问题："
echo "   1. 接受无穷大(inf)金额"
echo "   2. 接受NaN金额"
echo "   3. 接受超大金额(1e308)"
echo ""
echo "✅ 验证了以下安全特性工作正常："
echo "   - SQL注入防护"
echo "   - 负数金额拒绝"
echo "   - 零金额拒绝"
echo "   - 无效类型拒绝"
echo "   - 空值处理"
echo ""
echo "📖 详细信息请查看："
echo "   - FUZZING_REPORT.md (完整测试报告)"
echo "   - QUICK_START.md (快速开始指南)"
echo "   - README.md (详细文档)"
echo ""
echo "🔧 修复建议："
echo "   在 src/models/account_record.py 的 validate() 方法中"
echo "   添加 math.isnan() 和 math.isinf() 检查"
echo ""
echo "=========================================="
