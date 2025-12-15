#!/usr/bin/env python3
"""
Generate and test crash cases for demonstration
This script creates specific test cases that expose vulnerabilities
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from models.account_record import AccountRecord
from services.query_service import QueryService
from data.data_manager import DataManager
import tempfile
import shutil

def test_case_1_infinity_amount():
    """Test Case 1: Infinity amount value"""
    print("=" * 60)
    print("测试用例 1: 无穷大金额")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_001",
            type="INCOME",
            amount=float('inf'),  # Infinity
            date="2025-01-01T00:00:00"
        )
        
        print(f"创建记录: amount={record.amount}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了无穷大的金额！")
            print("建议: 应该拒绝inf和-inf值")
        else:
            print("✓ validate()正确拒绝了无穷大金额")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_2_nan_amount():
    """Test Case 2: NaN amount value"""
    print("=" * 60)
    print("测试用例 2: NaN（Not a Number）金额")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_002",
            type="EXPENDITURE",
            amount=float('nan'),  # NaN
            date="2025-01-01T00:00:00"
        )
        
        print(f"创建记录: amount={record.amount}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        # NaN comparisons are tricky
        if result:
            print("⚠️  问题: validate()接受了NaN金额！")
            print("建议: 应该使用math.isnan()检查")
        else:
            print("✓ validate()正确拒绝了NaN金额")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_3_negative_amount():
    """Test Case 3: Negative amount"""
    print("=" * 60)
    print("测试用例 3: 负数金额")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_003",
            type="INCOME",
            amount=-100.0,  # Negative
            date="2025-01-01T00:00:00"
        )
        
        print(f"创建记录: amount={record.amount}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了负数金额！")
        else:
            print("✓ validate()正确拒绝了负数金额")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_4_zero_amount():
    """Test Case 4: Zero amount"""
    print("=" * 60)
    print("测试用例 4: 零金额")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_004",
            type="INCOME",
            amount=0.0,  # Zero
            date="2025-01-01T00:00:00"
        )
        
        print(f"创建记录: amount={record.amount}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了零金额！")
        else:
            print("✓ validate()正确拒绝了零金额")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_5_invalid_type():
    """Test Case 5: Invalid record type"""
    print("=" * 60)
    print("测试用例 5: 无效的记录类型")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_005",
            type="INVALID_TYPE",  # Invalid
            amount=100.0,
            date="2025-01-01T00:00:00"
        )
        
        print(f"创建记录: type={record.type}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了无效的类型！")
        else:
            print("✓ validate()正确拒绝了无效类型")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_6_empty_date():
    """Test Case 6: Empty date string"""
    print("=" * 60)
    print("测试用例 6: 空日期字符串")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_006",
            type="INCOME",
            amount=100.0,
            date=""  # Empty
        )
        
        print(f"创建记录: date='{record.date}'")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了空日期！")
        else:
            print("✓ validate()正确拒绝了空日期")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_7_none_date():
    """Test Case 7: None date"""
    print("=" * 60)
    print("测试用例 7: None日期")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_007",
            type="INCOME",
            amount=100.0,
            date=None  # None
        )
        
        print(f"创建记录: date={record.date}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了None日期！")
        else:
            print("✓ validate()正确拒绝了None日期")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_8_sql_injection():
    """Test Case 8: SQL Injection attempt"""
    print("=" * 60)
    print("测试用例 8: SQL注入测试")
    print("=" * 60)
    
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_sql.db")
    
    try:
        dm = DataManager(db_path=db_path)
        
        # Try SQL injection in order_by parameter
        malicious_order_by = "date; DROP TABLE records--"
        print(f"尝试SQL注入: order_by='{malicious_order_by}'")
        
        try:
            results = dm.query_records(order_by=malicious_order_by)
            print("⚠️  查询执行了（可能存在SQL注入风险）")
            
            # Check if table still exists
            dm.driver.execute("SELECT COUNT(*) FROM records")
            print("✓ records表仍然存在，SQL注入被阻止")
            
        except Exception as e:
            print(f"查询失败: {type(e).__name__}: {e}")
            print("✓ SQL注入被阻止（查询失败）")
        
        dm.close()
        
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print()
    return False

def test_case_9_sort_empty_list():
    """Test Case 9: Sort empty list"""
    print("=" * 60)
    print("测试用例 9: 排序空列表")
    print("=" * 60)
    
    try:
        class MockDM:
            def query_records(self, **kwargs):
                return []
        
        qs = QueryService(MockDM())
        result = qs.sort_records([])
        print(f"排序结果: {result}")
        print("✓ 成功处理空列表")
        
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def test_case_10_very_large_amount():
    """Test Case 10: Very large amount"""
    print("=" * 60)
    print("测试用例 10: 超大金额")
    print("=" * 60)
    
    try:
        record = AccountRecord(
            id="test_010",
            type="INCOME",
            amount=1e308,  # Near max float
            date="2025-01-01T00:00:00"
        )
        
        print(f"创建记录: amount={record.amount}")
        result = record.validate()
        print(f"验证结果: {result}")
        
        if result:
            print("⚠️  问题: validate()接受了超大金额！")
            print("建议: 应该设置合理的金额上限")
        else:
            print("✓ validate()正确拒绝了超大金额")
            
    except Exception as e:
        print(f"💥 崩溃: {type(e).__name__}: {e}")
        return True
    
    print()
    return False

def main():
    print("\n")
    print("🔍 Account项目模糊测试 - 崩溃用例生成器")
    print("=" * 60)
    print()
    
    crash_count = 0
    issue_count = 0
    
    # Run all test cases
    test_cases = [
        test_case_1_infinity_amount,
        test_case_2_nan_amount,
        test_case_3_negative_amount,
        test_case_4_zero_amount,
        test_case_5_invalid_type,
        test_case_6_empty_date,
        test_case_7_none_date,
        test_case_8_sql_injection,
        test_case_9_sort_empty_list,
        test_case_10_very_large_amount,
    ]
    
    for test in test_cases:
        crashed = test()
        if crashed:
            crash_count += 1
    
    # Summary
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试用例: {len(test_cases)}")
    print(f"发现崩溃: {crash_count}")
    print(f"发现问题: 请查看上面的⚠️标记")
    print()
    print("建议的改进：")
    print("1. 在validate()中添加对inf/nan的检查")
    print("2. 确保金额有合理的上下限")
    print("3. 加强日期格式验证")
    print("4. 继续使用参数化SQL查询防止注入")
    print("=" * 60)

if __name__ == "__main__":
    main()
