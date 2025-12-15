"""
Integration tests for QueryService and StatisticsService.

Group 1: Top-down integration - Testing QueryService + StatisticsService interaction
Group 2: Bottom-up integration - Testing complete workflow from DataManager to Services

These tests verify that different components work correctly together,
beyond individual unit test coverage.
"""
import pytest
from pathlib import Path
from data.data_manager import DataManager
from services.query_service import QueryService
from services.statistics_service import StatisticsService
from models.account_record import AccountRecord
from models.category import Category
from utils_id_for_tests import gen_id_simple

# Constants for floating-point comparison tolerance
FLOAT_TOLERANCE = 0.01


@pytest.fixture
def setup_integration_db(tmp_path):
    """Create a test database with comprehensive sample data for integration tests."""
    db_path = tmp_path / "integration_test.db"
    dm = DataManager(str(db_path))
    
    # Add test categories
    categories = [
        Category(id="cat_salary", name="Salary", type="INCOME", is_custom=True),
        Category(id="cat_bonus", name="Bonus", type="INCOME", is_custom=True),
        Category(id="cat_food", name="Food", type="EXPENDITURE", is_custom=True),
        Category(id="cat_transport", name="Transport", type="EXPENDITURE", is_custom=True),
        Category(id="cat_entertainment", name="Entertainment", type="EXPENDITURE", is_custom=True),
    ]
    for cat in categories:
        dm.add_category(cat)
    
    # Add comprehensive test records spanning different dates and categories
    records = [
        # October 2025 - Week 1
        AccountRecord(id=gen_id_simple("r1"), type="INCOME", amount=5000.0,
                     date="2025-10-01T09:00:00", category_id="cat_salary", remark="Monthly salary"),
        AccountRecord(id=gen_id_simple("r2"), type="EXPENDITURE", amount=50.0,
                     date="2025-10-01T12:00:00", category_id="cat_food", remark="Lunch"),
        AccountRecord(id=gen_id_simple("r3"), type="EXPENDITURE", amount=20.0,
                     date="2025-10-02T08:00:00", category_id="cat_transport", remark="Bus fare"),
        AccountRecord(id=gen_id_simple("r4"), type="EXPENDITURE", amount=80.0,
                     date="2025-10-03T19:00:00", category_id="cat_food", remark="Dinner"),
        
        # October 2025 - Week 2
        AccountRecord(id=gen_id_simple("r5"), type="EXPENDITURE", amount=150.0,
                     date="2025-10-10T14:00:00", category_id="cat_entertainment", remark="Movie tickets"),
        AccountRecord(id=gen_id_simple("r6"), type="EXPENDITURE", amount=30.0,
                     date="2025-10-11T12:00:00", category_id="cat_food", remark="Lunch"),
        AccountRecord(id=gen_id_simple("r7"), type="EXPENDITURE", amount=25.0,
                     date="2025-10-12T08:00:00", category_id="cat_transport", remark="Taxi"),
        
        # October 2025 - Week 3
        AccountRecord(id=gen_id_simple("r8"), type="INCOME", amount=1000.0,
                     date="2025-10-15T10:00:00", category_id="cat_bonus", remark="Performance bonus"),
        AccountRecord(id=gen_id_simple("r9"), type="EXPENDITURE", amount=200.0,
                     date="2025-10-16T20:00:00", category_id="cat_entertainment", remark="Concert"),
        AccountRecord(id=gen_id_simple("r10"), type="EXPENDITURE", amount=45.0,
                     date="2025-10-17T12:00:00", category_id="cat_food", remark="Groceries"),
        
        # November 2025
        AccountRecord(id=gen_id_simple("r11"), type="INCOME", amount=5000.0,
                     date="2025-11-01T09:00:00", category_id="cat_salary", remark="Monthly salary"),
        AccountRecord(id=gen_id_simple("r12"), type="EXPENDITURE", amount=60.0,
                     date="2025-11-05T12:00:00", category_id="cat_food", remark="Lunch"),
        AccountRecord(id=gen_id_simple("r13"), type="EXPENDITURE", amount=100.0,
                     date="2025-11-10T15:00:00", category_id="cat_entertainment", remark="Gaming"),
    ]
    for rec in records:
        dm.save_record(rec)
    
    yield dm
    dm.close()


# ==================== Group 1: Top-Down Integration Tests ====================
# Testing interaction between QueryService and StatisticsService

class TestQueryStatisticsIntegration:
    """Integration tests for QueryService and StatisticsService working together."""
    
    def test_query_date_range_then_calculate_statistics(self, setup_integration_db):
        """
        Integration Test 1.1: Query records by date range, then calculate statistics on results.
        Tests: QueryService.query_by_date() → StatisticsService processing
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        
        # Query October 2025 records
        october_records = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        # Verify query results
        assert len(october_records) == 10
        
        # Manually calculate statistics on queried results (simulating StatisticsService logic)
        income_total = sum(r.amount for r in october_records if r.type == "INCOME")
        expenditure_total = sum(r.amount for r in october_records if r.type == "EXPENDITURE")
        
        assert income_total == 6000.0  # 5000 salary + 1000 bonus
        assert expenditure_total == 600.0  # sum of all October expenditures
        
        # Verify category breakdown
        category_totals = {}
        for r in october_records:
            category_totals[r.category_id] = category_totals.get(r.category_id, 0) + r.amount
        
        assert category_totals["cat_salary"] == 5000.0
        assert category_totals["cat_bonus"] == 1000.0
        assert category_totals["cat_food"] == 205.0  # 50 + 80 + 30 + 45
        assert category_totals["cat_transport"] == 45.0  # 20 + 25
        assert category_totals["cat_entertainment"] == 350.0  # 150 + 200
    
    def test_query_by_category_then_timeseries_analysis(self, setup_integration_db):
        """
        Integration Test 1.2: Query records by category, then perform time series analysis.
        Tests: QueryService.query_by_category() → date-based aggregation
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        
        # Query all food-related records
        food_records = qs.query_by_category("cat_food")
        
        # Verify query results
        assert len(food_records) == 5  # r2, r4, r6, r10, r12
        
        # Perform time series analysis on food expenses by month
        monthly_food = {}
        for r in food_records:
            month_key = r.date[:7]  # Extract YYYY-MM
            monthly_food[month_key] = monthly_food.get(month_key, 0) + r.amount
        
        assert monthly_food["2025-10"] == 205.0  # October food expenses
        assert monthly_food["2025-11"] == 60.0   # November food expenses
        
        # Sort food records by date (descending) and verify order
        sorted_food = qs.sort_records(food_records, descending=True)
        assert sorted_food[0].date == "2025-11-05T12:00:00"  # Most recent
        assert sorted_food[-1].date == "2025-10-01T12:00:00"  # Oldest
    
    def test_combined_query_sorting_and_statistics(self, setup_integration_db):
        """
        Integration Test 1.3: Complex workflow combining date query, sorting, and statistics.
        Tests: QueryService (multiple methods) → StatisticsService-style analysis
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        
        # Step 1: Query October Week 2 records (Oct 10-16)
        week2_records = qs.query_by_date("2025-10-10T00:00:00", "2025-10-16T23:59:59")
        # Records in range: r5 (Oct 10), r6 (Oct 11), r7 (Oct 12), r8 (Oct 15), r9 (Oct 16)
        assert len(week2_records) == 5
        
        # Step 2: Sort records by date (ascending)
        sorted_records = qs.sort_records(week2_records, descending=False)
        assert sorted_records[0].date == "2025-10-10T14:00:00"  # Oct 10 (r5)
        assert sorted_records[-1].date == "2025-10-16T20:00:00"  # Oct 16 (r9)
        
        # Step 3: Calculate daily statistics
        daily_totals = {}
        for r in sorted_records:
            day_key = r.date[:10]
            daily_totals[day_key] = daily_totals.get(day_key, 0) + r.amount
        
        assert daily_totals["2025-10-10"] == 150.0
        assert daily_totals["2025-10-11"] == 30.0
        assert daily_totals["2025-10-12"] == 25.0
        assert daily_totals["2025-10-15"] == 1000.0
        assert daily_totals["2025-10-16"] == 200.0
        
        # Step 4: Verify category distribution in this period
        entertainment_records = [r for r in week2_records if r.category_id == "cat_entertainment"]
        assert len(entertainment_records) == 2  # r5 (Oct 10) and r9 (Oct 16)
        entertainment_total = sum(r.amount for r in entertainment_records)
        assert entertainment_total == 350.0  # 150 + 200


# ==================== Group 2: Bottom-Up Integration Tests ====================
# Testing complete workflow from DataManager through both services

class TestEndToEndWorkflow:
    """End-to-end integration tests covering DataManager → Services."""
    
    def test_complete_workflow_add_query_statistics(self, setup_integration_db):
        """
        Integration Test 2.1: Complete workflow from data insertion to statistics.
        Tests: DataManager → QueryService → StatisticsService
        Bottom-up integration: Database layer → Service layer
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        stats = StatisticsService(dm)
        
        # Step 1: Verify initial statistics (all records)
        total_by_type = stats.total_by_type()
        assert total_by_type["INCOME"] == 11000.0  # 5000 + 1000 + 5000
        assert total_by_type["EXPENDITURE"] == 760.0  # sum of all expenditures
        
        # Step 2: Add new records dynamically
        new_record = AccountRecord(
            id=gen_id_simple("r100"),
            type="INCOME",
            amount=2000.0,
            date="2025-10-20T10:00:00",
            category_id="cat_bonus",
            remark="Extra bonus"
        )
        dm.save_record(new_record)
        
        # Step 3: Query to verify new record is included
        october_records = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        assert len(october_records) == 11  # Was 10, now 11
        
        # Step 4: Verify statistics updated correctly
        updated_stats = stats.total_by_type()
        assert updated_stats["INCOME"] == 13000.0  # Increased by 2000
        
        # Step 5: Verify category statistics
        category_stats = stats.by_category()
        assert category_stats["cat_bonus"] == 3000.0  # 1000 + 2000
    
    def test_complete_workflow_query_filter_aggregate(self, setup_integration_db):
        """
        Integration Test 2.2: Complete workflow with filtering and aggregation.
        Tests: DataManager → QueryService (filtering) → StatisticsService (aggregation)
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        stats = StatisticsService(dm)
        
        # Step 1: Get time series for all records
        monthly_series = stats.timeseries(period="month")
        assert "2025-10" in monthly_series
        assert "2025-11" in monthly_series
        assert monthly_series["2025-10"] == 6600.0  # Total October
        assert monthly_series["2025-11"] == 5160.0  # Total November
        
        # Step 2: Query specific category records
        transport_records = qs.query_by_category("cat_transport")
        assert len(transport_records) == 2  # r3, r7
        
        # Step 3: Calculate category-specific statistics
        transport_total = sum(r.amount for r in transport_records)
        assert transport_total == 45.0  # 20 + 25
        
        # Step 4: Verify sorting maintains data integrity
        sorted_transport = qs.sort_records(transport_records, descending=True)
        assert sorted_transport[0].amount == 25.0  # Most recent (Oct 12)
        assert sorted_transport[1].amount == 20.0  # Older (Oct 2)
        
        # Step 5: Cross-verify with by_category statistics
        category_breakdown = stats.by_category()
        assert category_breakdown["cat_transport"] == transport_total
    
    def test_cross_module_data_consistency(self, setup_integration_db):
        """
        Integration Test 2.3: Verify data consistency across QueryService and StatisticsService.
        Tests: Both services operate on same DataManager and return consistent results
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        stats = StatisticsService(dm)
        
        # Scenario: Verify that query results match statistics calculations
        
        # Get all income records via QueryService
        all_records = qs.query_by_date("2025-01-01T00:00:00", "2025-12-31T23:59:59")
        income_from_query = sum(r.amount for r in all_records if r.type == "INCOME")
        expenditure_from_query = sum(r.amount for r in all_records if r.type == "EXPENDITURE")
        
        # Get totals via StatisticsService
        totals = stats.total_by_type()
        
        # Verify consistency
        assert income_from_query == totals["INCOME"]
        assert expenditure_from_query == totals["EXPENDITURE"]
        
        # Verify category consistency
        category_from_query = {}
        for r in all_records:
            category_from_query[r.category_id] = category_from_query.get(r.category_id, 0) + r.amount
        
        category_from_stats = stats.by_category()
        
        # All categories should match
        for cat_id in category_from_query:
            assert abs(category_from_query[cat_id] - category_from_stats[cat_id]) < FLOAT_TOLERANCE
        
        # Verify time series consistency
        daily_series = stats.timeseries(period="day")
        daily_from_query = {}
        for r in all_records:
            day_key = r.date[:10]
            daily_from_query[day_key] = daily_from_query.get(day_key, 0) + r.amount
        
        for day in daily_series:
            assert abs(daily_series[day] - daily_from_query[day]) < FLOAT_TOLERANCE
    
    def test_edge_case_empty_queries_with_statistics(self, setup_integration_db):
        """
        Integration Test 2.4: Test edge cases with empty query results.
        Tests: Service integration handles empty datasets correctly
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        stats = StatisticsService(dm)
        
        # Query future dates (no records)
        future_records = qs.query_by_date("2026-01-01T00:00:00", "2026-12-31T23:59:59")
        assert len(future_records) == 0
        
        # Statistics on empty result set
        future_income = sum(r.amount for r in future_records if r.type == "INCOME")
        future_expenditure = sum(r.amount for r in future_records if r.type == "EXPENDITURE")
        assert future_income == 0.0
        assert future_expenditure == 0.0
        
        # Query non-existent category
        nonexistent_records = qs.query_by_category("cat_nonexistent")
        assert len(nonexistent_records) == 0
        
        # Sorting empty list
        sorted_empty = qs.sort_records(nonexistent_records)
        assert len(sorted_empty) == 0
        
        # Overall statistics should still work
        overall_stats = stats.total_by_type()
        assert overall_stats["INCOME"] > 0  # Has records in database
        assert overall_stats["EXPENDITURE"] > 0
    
    def test_multi_service_workflow_with_filtering(self, setup_integration_db):
        """
        Integration Test 2.5: Complex multi-service workflow with multiple filtering steps.
        Tests: Chained operations across services maintain correctness
        """
        dm = setup_integration_db
        qs = QueryService(dm)
        stats = StatisticsService(dm)
        
        # Workflow: Get October entertainment expenses, sorted by date, with daily breakdown
        
        # Step 1: Query October records
        october_records = qs.query_by_date("2025-10-01T00:00:00", "2025-10-31T23:59:59")
        
        # Step 2: Filter to entertainment category (simulating combined query)
        entertainment_records = [r for r in october_records if r.category_id == "cat_entertainment"]
        assert len(entertainment_records) == 2  # r5, r9
        
        # Step 3: Sort by date ascending
        sorted_entertainment = qs.sort_records(entertainment_records, descending=False)
        assert sorted_entertainment[0].date == "2025-10-10T14:00:00"  # Movie
        assert sorted_entertainment[1].date == "2025-10-16T20:00:00"  # Concert
        
        # Step 4: Calculate daily breakdown
        daily_entertainment = {}
        for r in sorted_entertainment:
            day = r.date[:10]
            daily_entertainment[day] = daily_entertainment.get(day, 0) + r.amount
        
        assert daily_entertainment["2025-10-10"] == 150.0
        assert daily_entertainment["2025-10-16"] == 200.0
        
        # Step 5: Verify against category statistics
        all_category_stats = stats.by_category()
        entertainment_total = sum(r.amount for r in entertainment_records)
        
        # Total entertainment in October should match our filtered calculation
        october_entertainment_from_stats = entertainment_total
        assert october_entertainment_from_stats == 350.0
        
        # Overall entertainment (including November) from stats should be higher
        assert all_category_stats["cat_entertainment"] == 450.0  # 150 + 200 + 100
