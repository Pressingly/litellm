import pytest
import asyncio
from datetime import datetime
from ..models import LagoSubscription
from ..billing_logger import BillingLogger
from ..db_service import SubscriptionDBService
import asyncpg
import os
from unittest.mock import Mock, patch

@pytest.fixture
async def db_pool():
    """Create a test database pool"""
    pool = await asyncpg.create_pool(
        os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db")
    )
    yield pool
    await pool.close()

@pytest.fixture
def subscription():
    """Create a test subscription"""
    return LagoSubscription(
        customer_id="test-customer",
        plan_id="test-plan",
        balance_threshold={"credit": 10},
        remaining_balance={"credit": 100}
    )

@pytest.fixture
def billing_logger():
    """Create a test billing logger"""
    return BillingLogger(
        lago_api_key="test-key",
        lago_url="http://test.lago.com"
    )

@pytest.mark.asyncio
async def test_subscription_creation(db_pool, subscription):
    """Test creating a subscription"""
    service = SubscriptionDBService(db_pool)
    await service.create_subscription(subscription)
    
    # Verify subscription was created
    saved_subscription = await service.get_subscription(subscription.id)
    assert saved_subscription is not None
    assert saved_subscription.customer_id == subscription.customer_id
    assert saved_subscription.plan_id == subscription.plan_id

@pytest.mark.asyncio
async def test_subscription_status_update(db_pool, subscription):
    """Test updating subscription status based on balance"""
    service = SubscriptionDBService(db_pool)
    await service.create_subscription(subscription)
    
    # Update balance below threshold
    subscription.remaining_balance = {"credit": 5}
    subscription.update_remaining_balance(subscription.remaining_balance)
    await service.update_subscription(subscription)
    
    # Verify status was updated
    updated = await service.get_subscription(subscription.id)
    assert updated.status == "suspended"

@pytest.mark.asyncio
async def test_billing_logger_pre_check(billing_logger):
    """Test pre-call check in billing logger"""
    # Test with missing subscription ID
    result = await billing_logger.async_pre_call_check({"headers": {}})
    assert result is not None
    assert result["status_code"] == 400
    
    # Test with valid subscription ID
    result = await billing_logger.async_pre_call_check({
        "headers": {"x-openwebui-subscription-id": "test-sub"}
    })
    assert result is None

@pytest.mark.asyncio
async def test_billing_logger_success_event(billing_logger):
    """Test success event handling in billing logger"""
    mock_response = Mock()
    mock_response.cost = 0.5
    
    # Mock httpx client
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "subscription_remaining_balance": [{
                "billable_metric_id": "test-metric",
                "total_usage": 100,
                "total_deposited_credits": 1000,
                "remaining_balance": 900
            }]
        }
        
        await billing_logger.async_log_success_event(
            {"headers": {"x-openwebui-subscription-id": "test-sub"}},
            mock_response,
            datetime.now().timestamp(),
            datetime.now().timestamp()
        )
        
        # Verify Lago API was called
        mock_post.assert_called_once() 