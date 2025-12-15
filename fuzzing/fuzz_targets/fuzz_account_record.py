#!/usr/bin/env python3
"""
Fuzzing target for AccountRecord validation
Tests the AccountRecord.validate() method with random inputs
"""

import sys
import atheris
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from models.account_record import AccountRecord


def TestOneInput(data):
    """
    Fuzz target that creates AccountRecord instances with random data
    and calls validate() to find crashes or bugs
    """
    fdp = atheris.FuzzedDataProvider(data)
    
    try:
        # Generate random fields for AccountRecord
        record_id = fdp.ConsumeUnicodeNoSurrogates(20)
        record_type = fdp.ConsumeUnicodeNoSurrogates(20)
        
        # Try to consume a float, might be invalid
        amount_bytes = fdp.ConsumeBytes(8)
        try:
            amount = float(fdp.ConsumeFloat())
        except:
            amount = 0.0
            
        date_str = fdp.ConsumeUnicodeNoSurrogates(50)
        category_id = fdp.ConsumeUnicodeNoSurrogates(20) if fdp.ConsumeBool() else None
        remark = fdp.ConsumeUnicodeNoSurrogates(100) if fdp.ConsumeBool() else None
        created_at = fdp.ConsumeUnicodeNoSurrogates(50) if fdp.ConsumeBool() else None
        
        # Create AccountRecord with fuzzed data
        record = AccountRecord(
            id=record_id,
            type=record_type,
            amount=amount,
            date=date_str,
            category_id=category_id,
            remark=remark,
            created_at=created_at
        )
        
        # Call validate - this is where bugs might be found
        result = record.validate()
        
        # Try to access fields after validation
        _ = record.id
        _ = record.type
        _ = record.amount
        _ = record.date
        
    except (ValueError, TypeError, AttributeError) as e:
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
