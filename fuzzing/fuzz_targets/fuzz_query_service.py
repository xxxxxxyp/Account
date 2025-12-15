#!/usr/bin/env python3
"""
Fuzzing target for QueryService
Tests query and sorting functions with random inputs
"""

import sys
import atheris
import os
from datetime import datetime

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.account_record import AccountRecord
from services.query_service import QueryService


class MockDataManager:
    """Mock DataManager for testing without database"""
    
    def __init__(self):
        self.records = []
    
    def query_records(self, start=None, end=None, category_id=None, **kwargs):
        """Return filtered records based on parameters"""
        results = self.records[:]
        
        if start:
            results = [r for r in results if r.date >= start]
        if end:
            results = [r for r in results if r.date <= end]
        if category_id:
            results = [r for r in results if r.category_id == category_id]
            
        return results


def TestOneInput(data):
    """
    Fuzz target that tests QueryService with random data
    """
    fdp = atheris.FuzzedDataProvider(data)
    
    try:
        # Create mock data manager
        dm = MockDataManager()
        
        # Add some random records
        num_records = fdp.ConsumeIntInRange(0, 10)
        for i in range(num_records):
            try:
                # Generate amount, handling special float values
                raw_amount = fdp.ConsumeFloat()
                # Use raw float to test edge cases (inf, nan, etc)
                amount = raw_amount if fdp.ConsumeBool() else abs(raw_amount)
                
                record = AccountRecord(
                    id=fdp.ConsumeUnicodeNoSurrogates(10),
                    type=fdp.PickValueInList(["INCOME", "EXPENDITURE", fdp.ConsumeUnicodeNoSurrogates(10)]),
                    amount=amount,
                    date=fdp.ConsumeUnicodeNoSurrogates(30),
                    category_id=fdp.ConsumeUnicodeNoSurrogates(10) if fdp.ConsumeBool() else None,
                    remark=fdp.ConsumeUnicodeNoSurrogates(50) if fdp.ConsumeBool() else None
                )
                dm.records.append(record)
            except (ValueError, TypeError):
                pass
        
        # Create QueryService
        qs = QueryService(dm)
        
        # Test query_by_date
        start_date = fdp.ConsumeUnicodeNoSurrogates(30)
        end_date = fdp.ConsumeUnicodeNoSurrogates(30)
        results = qs.query_by_date(start_date, end_date)
        
        # Test query_by_category
        category = fdp.ConsumeUnicodeNoSurrogates(20)
        results = qs.query_by_category(category)
        
        # Test sort_records with random records
        descending = fdp.ConsumeBool()
        if dm.records:
            sorted_results = qs.sort_records(dm.records, descending=descending)
            # Access sorted results
            for rec in sorted_results[:3]:  # Check first 3
                _ = rec.date
                _ = rec.id
                
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        # Expected exceptions - these are OK
        pass
    except Exception as e:
        # Unexpected exceptions - might indicate bugs
        print(f"Unexpected exception: {type(e).__name__}: {e}")
        raise


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
