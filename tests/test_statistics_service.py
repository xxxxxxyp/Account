"""
Unit tests for StatisticsService.
Tests cover total_by_type(), by_category(), and timeseries() methods.
"""
import pytest
from pathlib import Path
from data.data_manager import DataManager
from services.statistics_service import StatisticsService
from models.account_record import AccountRecord
from models.category import Category
from utils_id_for_tests import gen_id_simple


@pytest.fixture
def setup_test_db(tmp_path):
    """Create a test database with sample data."""
    db_path = tmp_path / "stats_test.db"
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


class TestStatisticsService:
    """Test suite for StatisticsService class."""
    
    # ==================== Tests for total_by_type() ====================
    
    def test_total_by_type_empty_database(self, setup_test_db):
        """Test total_by_type with no records."""
        dm = setup_test_db
        stats = StatisticsService(dm)
        result = stats.total_by_type()
        
        assert result["INCOME"] == 0.0
        assert result["EXPENDITURE"] == 0.0
    
    def test_total_by_type_only_income(self, setup_test_db):
        """Test total_by_type with only income records."""
        dm = setup_test_db
        # Add income records
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="INCOME", amount=1000.0, 
                            date="2025-10-01T10:00:00", category_id="cat_salary")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="INCOME", amount=500.0, 
                            date="2025-10-02T10:00:00", category_id="cat_salary")
        dm.save_record(rec1)
        dm.save_record(rec2)
        
        stats = StatisticsService(dm)
        result = stats.total_by_type()
        
        assert result["INCOME"] == 1500.0
        assert result["EXPENDITURE"] == 0.0
    
    def test_total_by_type_only_expenditure(self, setup_test_db):
        """Test total_by_type with only expenditure records."""
        dm = setup_test_db
        # Add expenditure records
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-01T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-02T12:00:00", category_id="cat_transport")
        dm.save_record(rec1)
        dm.save_record(rec2)
        
        stats = StatisticsService(dm)
        result = stats.total_by_type()
        
        assert result["INCOME"] == 0.0
        assert result["EXPENDITURE"] == 80.0
    
    def test_total_by_type_mixed_records(self, setup_test_db):
        """Test total_by_type with both income and expenditure records."""
        dm = setup_test_db
        # Add mixed records
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="INCOME", amount=2000.0, 
                            date="2025-10-01T10:00:00", category_id="cat_salary")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=100.0, 
                            date="2025-10-02T12:00:00", category_id="cat_food")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-03T12:00:00", category_id="cat_transport")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.total_by_type()
        
        assert result["INCOME"] == 2000.0
        assert result["EXPENDITURE"] == 150.0
    
    def test_total_by_type_decimal_amounts(self, setup_test_db):
        """Test total_by_type with decimal amounts."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="INCOME", amount=123.45, 
                            date="2025-10-01T10:00:00", category_id="cat_salary")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=67.89, 
                            date="2025-10-02T12:00:00", category_id="cat_food")
        dm.save_record(rec1)
        dm.save_record(rec2)
        
        stats = StatisticsService(dm)
        result = stats.total_by_type()
        
        assert abs(result["INCOME"] - 123.45) < 0.01
        assert abs(result["EXPENDITURE"] - 67.89) < 0.01
    
    # ==================== Tests for by_category() ====================
    
    def test_by_category_empty_database(self, setup_test_db):
        """Test by_category with no records."""
        dm = setup_test_db
        stats = StatisticsService(dm)
        result = stats.by_category()
        
        assert len(result) == 0
    
    def test_by_category_single_category(self, setup_test_db):
        """Test by_category with records in single category."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-01T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-02T12:00:00", category_id="cat_food")
        dm.save_record(rec1)
        dm.save_record(rec2)
        
        stats = StatisticsService(dm)
        result = stats.by_category()
        
        assert len(result) == 1
        assert result["cat_food"] == 80.0
    
    def test_by_category_multiple_categories(self, setup_test_db):
        """Test by_category with records across multiple categories."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-01T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-02T12:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-10-03T10:00:00", category_id="cat_salary")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.by_category()
        
        assert len(result) == 3
        assert result["cat_food"] == 50.0
        assert result["cat_transport"] == 30.0
        assert result["cat_salary"] == 1000.0
    
    def test_by_category_aggregates_same_category(self, setup_test_db):
        """Test by_category aggregates multiple records in same category."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=25.0, 
                            date="2025-10-01T12:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=35.0, 
                            date="2025-10-02T12:00:00", category_id="cat_food")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="EXPENDITURE", amount=40.0, 
                            date="2025-10-03T12:00:00", category_id="cat_food")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.by_category()
        
        assert len(result) == 1
        assert result["cat_food"] == 100.0
    
    # ==================== Tests for timeseries() ====================
    
    def test_timeseries_empty_database(self, setup_test_db):
        """Test timeseries with no records."""
        dm = setup_test_db
        stats = StatisticsService(dm)
        result = stats.timeseries(period="day")
        
        assert len(result) == 0
    
    def test_timeseries_by_day(self, setup_test_db):
        """Test timeseries aggregation by day."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-01T10:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-01T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="EXPENDITURE", amount=20.0, 
                            date="2025-10-02T12:00:00", category_id="cat_food")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.timeseries(period="day")
        
        assert len(result) == 2
        assert result["2025-10-01"] == 80.0
        assert result["2025-10-02"] == 20.0
    
    def test_timeseries_by_month(self, setup_test_db):
        """Test timeseries aggregation by month."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=100.0, 
                            date="2025-10-05T10:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=200.0, 
                            date="2025-10-15T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=1000.0, 
                            date="2025-11-01T12:00:00", category_id="cat_salary")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.timeseries(period="month")
        
        assert len(result) == 2
        assert result["2025-10"] == 300.0
        assert result["2025-11"] == 1000.0
    
    def test_timeseries_by_year(self, setup_test_db):
        """Test timeseries aggregation by year."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=100.0, 
                            date="2024-12-31T10:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=200.0, 
                            date="2025-01-01T14:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="INCOME", amount=3000.0, 
                            date="2025-06-15T12:00:00", category_id="cat_salary")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.timeseries(period="year")
        
        assert len(result) == 2
        assert result["2024"] == 100.0
        assert result["2025"] == 3200.0
    
    def test_timeseries_default_period(self, setup_test_db):
        """Test timeseries with default period (should be day)."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=50.0, 
                            date="2025-10-01T10:00:00", category_id="cat_food")
        dm.save_record(rec1)
        
        stats = StatisticsService(dm)
        result = stats.timeseries()  # default period
        
        assert "2025-10-01" in result
        assert result["2025-10-01"] == 50.0
    
    def test_timeseries_aggregates_same_period(self, setup_test_db):
        """Test timeseries correctly aggregates multiple records in same period."""
        dm = setup_test_db
        rec1 = AccountRecord(id=gen_id_simple("r1"), type="EXPENDITURE", amount=10.0, 
                            date="2025-10-01T08:00:00", category_id="cat_food")
        rec2 = AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=20.0, 
                            date="2025-10-01T12:00:00", category_id="cat_transport")
        rec3 = AccountRecord(id=gen_id_simple("r3"), type="EXPENDITURE", amount=30.0, 
                            date="2025-10-01T18:00:00", category_id="cat_food")
        dm.save_record(rec1)
        dm.save_record(rec2)
        dm.save_record(rec3)
        
        stats = StatisticsService(dm)
        result = stats.timeseries(period="day")
        
        assert len(result) == 1
        assert result["2025-10-01"] == 60.0
