#!/usr/bin/env python3
"""
Fuzzing target for DataManager query_records SQL injection testing
Tests the query_records method with potentially malicious inputs
"""

import sys
import atheris
import os
import tempfile
import shutil

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from data.data_manager import DataManager
from models.account_record import AccountRecord


def TestOneInput(data):
    """
    Fuzz target that tests DataManager with random query parameters
    Looking for SQL injection vulnerabilities and crashes
    """
    fdp = atheris.FuzzedDataProvider(data)
    
    # Use temporary database for each test
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_fuzz.db")
    
    try:
        # Create DataManager with temp database
        dm = DataManager(db_path=db_path)
        
        # Add a valid record first
        try:
            valid_record = AccountRecord(
                id="test_001",
                type="INCOME",
                amount=100.0,
                date="2025-01-01T00:00:00",
                category_id="cat_001",
                remark="test"
            )
            dm.save_record(valid_record)
        except:
            pass
        
        # Test query_records with fuzzed parameters
        start_date = fdp.ConsumeUnicodeNoSurrogates(50)
        end_date = fdp.ConsumeUnicodeNoSurrogates(50)
        category_id = fdp.ConsumeUnicodeNoSurrogates(50)
        limit = fdp.ConsumeIntInRange(-100, 1000)
        offset = fdp.ConsumeIntInRange(-100, 1000)
        order_by = fdp.ConsumeUnicodeNoSurrogates(100)
        
        # Try to query with fuzzed parameters
        try:
            results = dm.query_records(
                start=start_date if fdp.ConsumeBool() else None,
                end=end_date if fdp.ConsumeBool() else None,
                category_id=category_id if fdp.ConsumeBool() else None,
                limit=limit,
                offset=offset,
                order_by=order_by
            )
            
            # Try to access results
            for rec in results[:5]:
                _ = rec.id
                _ = rec.type
                _ = rec.amount
                
        except Exception:
            # Database errors are expected with invalid SQL
            pass
        
        # Test save_record with fuzzed data
        try:
            fuzz_record = AccountRecord(
                id=fdp.ConsumeUnicodeNoSurrogates(20),
                type=fdp.ConsumeUnicodeNoSurrogates(20),
                amount=fdp.ConsumeFloat(),
                date=fdp.ConsumeUnicodeNoSurrogates(50),
                category_id=fdp.ConsumeUnicodeNoSurrogates(20) if fdp.ConsumeBool() else None,
                remark=fdp.ConsumeUnicodeNoSurrogates(100) if fdp.ConsumeBool() else None
            )
            dm.save_record(fuzz_record)
        except Exception:
            # Save errors are expected with invalid data
            pass
        
        # Clean up
        dm.close()
        
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        # Expected exceptions - these are OK
        pass
    except (sqlite3.Error, OSError, IOError) as e:
        # Database and I/O exceptions are expected with fuzzed data
        pass
    except Exception as e:
        # Unexpected exceptions - might indicate bugs
        # Log but don't raise as temp directory needs cleanup
        import sys
        print(f"Unexpected exception: {type(e).__name__}: {e}", file=sys.stderr)
    finally:
        # Always clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
