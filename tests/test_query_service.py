"""
Unit tests for QueryService.
Tests cover query_by_date(), query_by_category(), and sort_records() methods.
"""
import pytest
from pathlib import Path
from data.data_manager import DataManager
from services.query_service import QueryService
from models.account_record import AccountRecord
from models.category import Category
from utils_id_for_tests import gen_id_simple


@pytest.fixture
def setup_test_db(tmp_path):
    """Create a test database with sample data."""
    db_path = tmp_path / "query_test.db"
    dm = DataManager(str(db_path))
    
    # Add test categories
    cat1 = Category(id="cat_food", name="Food", type="EXPENDITURE", is_custom=True)
    cat2 = Category(id="cat_salary", name="Salary", type="INCOME", is_custom=True)
    cat3 = Category(id="cat_transport", name="Transport", type="EXPENDITURE", is_custom=True)
    dm.add_category(cat1)
    dm.add_category(cat2)
    dm.add_category(cat3)
    
    yield dm
    dm.close()


class TestQueryService:
    """Test suite for QueryService class."""
    
    # ==================== Tests for query_by_date() ====================
    
    def test_query_by_date_empty_database(self, setup_test_db):
        """Test query_by_date with no records in database."""
        dm = setup_test_db
        qs = QueryService(dm)
        
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 0
    
    def test_query_by_date_no_matches(self, setup_test_db):
        """Test query_by_date with date range that has no matching records."""
        dm = setup_test_db
        # Add record outside the query range
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-09-15T12:00:00", category_id="cat_food")
        dm.save_record(rec)
        
        qs = QueryService(dm)
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 0
    
    def test_query_by_date_single_match(self, setup_test_db):
        """Test query_by_date with single matching record."""
        dm = setup_test_db
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-10-15T12:00:00", category_id="cat_food")
        dm.save_record(rec)
        
        qs = QueryService(dm)
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 1
        assert result[0].id == rec.id
        assert result[0].amount == 50.0
    
    def test_query_by_date_multiple_matches(self, setup_test_db):
        """Test query_by_date with multiple matching records."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-25T10:00:00", category_id="cat_salary")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        qs = QueryService(dm)
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 3
    
    def test_query_by_date_boundary_start(self, setup_test_db):
        """Test query_by_date includes record at start boundary."""
        dm = setup_test_db
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-10-01T00:00:00", category_id="cat_food")
        dm.save_record(rec)
        
        qs = QueryService(dm)
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 1
        assert result[0].id == rec.id
    
    def test_query_by_date_boundary_end(self, setup_test_db):
        """Test query_by_date includes record at end boundary."""
        dm = setup_test_db
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-10-31T23:59:59", category_id="cat_food")
        dm.save_record(rec)
        
        qs = QueryService(dm)
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 1
        assert result[0].id == rec.id
    
    def test_query_by_date_filters_outside_range(self, setup_test_db):
        """Test query_by_date excludes records outside the date range."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-09-30T23:59:59", category_id="cat_food")  # Before
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T12:00:00", category_id="cat_transport")  # Inside
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-11-01T00:00:00", category_id="cat_salary")  # After
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        qs = QueryService(dm)
        result = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        assert len(result) == 1
        assert result[0].id == rec2.id
    
    # ==================== Tests for query_by_category() ====================
    
    def test_query_by_category_empty_database(self, setup_test_db):
        """Test query_by_category with no records in database."""
        dm = setup_test_db
        qs = QueryService(dm)
        
        result = qs.query_by_category("cat_food")
        
        assert len(result) == 0
    
    def test_query_by_category_no_matches(self, setup_test_db):
        """Test query_by_category with category that has no records."""
        dm = setup_test_db
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-10-15T12:00:00", category_id="cat_food")
        dm.save_record(rec)
        
        qs = QueryService(dm)
        result = qs.query_by_category("cat_transport")
        
        assert len(result) == 0
    
    def test_query_by_category_single_match(self, setup_test_db):
        """Test query_by_category with single matching record."""
        dm = setup_test_db
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-10-15T12:00:00", category_id="cat_food")
        dm.save_record(rec)
        
        qs = QueryService(dm)
        result = qs.query_by_category("cat_food")
        
        assert len(result) == 1
        assert result[0].id == rec.id
        assert result[0].category_id == "cat_food"
    
    def test_query_by_category_multiple_matches(self, setup_test_db):
        """Test query_by_category with multiple matching records."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T14:00:00", category_id="cat_food")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="EXPENDITURE", amount=20.0, 
                            date="2025-10-25T10:00:00", category_id="cat_food")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        qs = QueryService(dm)
        result = qs.query_by_category("cat_food")
        
        assert len(result) == 3
        for r in result:
            assert r.category_id == "cat_food"
    
    def test_query_by_category_filters_other_categories(self, setup_test_db):
        """Test query_by_category excludes records from other categories."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-25T10:00:00", category_id="cat_salary")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        qs = QueryService(dm)
        result = qs.query_by_category("cat_transport")
        
        assert len(result) == 1
        assert result[0].id == rec2.id
        assert result[0].category_id == "cat_transport"
    
    # ==================== Tests for sort_records() ====================
    
    def test_sort_records_empty_list(self, setup_test_db):
        """Test sort_records with empty list."""
        dm = setup_test_db
        qs = QueryService(dm)
        
        result = qs.sort_records([])
        
        assert len(result) == 0
    
    def test_sort_records_single_record(self, setup_test_db):
        """Test sort_records with single record."""
        dm = setup_test_db
        rec = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                           date="2025-10-15T12:00:00", category_id="cat_food")
        
        qs = QueryService(dm)
        result = qs.sort_records([rec])
        
        assert len(result) == 1
        assert result[0].id == rec.id
    
    def test_sort_records_descending_default(self, setup_test_db):
        """Test sort_records sorts in descending order by default."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-10T10:00:00", category_id="cat_salary")
        
        qs = QueryService(dm)
        result = qs.sort_records([rec1, rec2, rec3])
        
        assert len(result) == 3
        # Descending: most recent first
        assert result[0].date == "2025-10-15T14:00:00"
        assert result[1].date == "2025-10-10T10:00:00"
        assert result[2].date == "2025-10-05T12:00:00"
    
    def test_sort_records_descending_explicit(self, setup_test_db):
        """Test sort_records sorts in descending order when explicitly specified."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-10T10:00:00", category_id="cat_salary")
        
        qs = QueryService(dm)
        result = qs.sort_records([rec1, rec2, rec3], descending=True)
        
        assert len(result) == 3
        assert result[0].date == "2025-10-15T14:00:00"
        assert result[1].date == "2025-10-10T10:00:00"
        assert result[2].date == "2025-10-05T12:00:00"
    
    def test_sort_records_ascending(self, setup_test_db):
        """Test sort_records sorts in ascending order."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-10T10:00:00", category_id="cat_salary")
        
        qs = QueryService(dm)
        result = qs.sort_records([rec1, rec2, rec3], descending=False)
        
        assert len(result) == 3
        # Ascending: oldest first
        assert result[0].date == "2025-10-05T12:00:00"
        assert result[1].date == "2025-10-10T10:00:00"
        assert result[2].date == "2025-10-15T14:00:00"
    
    def test_sort_records_same_date(self, setup_test_db):
        """Test sort_records handles records with same date."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-15T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-15T12:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-15T12:00:00", category_id="cat_salary")
        
        qs = QueryService(dm)
        result = qs.sort_records([rec1, rec2, rec3])
        
        assert len(result) == 3
        # All have same date, order should be stable
        for r in result:
            assert r.date == "2025-10-15T12:00:00"
    
    def test_sort_records_preserves_record_data(self, setup_test_db):
        """Test sort_records preserves all record data after sorting."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-05T12:00:00", category_id="cat_food", 
                            remark="Lunch")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="INCOME", amount=1000.0, 
                            date="2025-10-15T10:00:00", category_id="cat_salary", 
                            remark="Monthly salary")
        
        qs = QueryService(dm)
        result = qs.sort_records([rec1, rec2], descending=False)
        
        assert len(result) == 2
        assert result[0].id == rec1.id
        assert result[0].amount == 50.0
        assert result[0].remark == "Lunch"
        assert result[1].id == rec2.id
        assert result[1].amount == 1000.0
        assert result[1].remark == "Monthly salary"
