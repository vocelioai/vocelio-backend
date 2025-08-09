# apps/phone-numbers/tests/test_number_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session

from services.number_service import NumberService
from models.phone_number import PhoneNumber
from schemas.phone_number import PhoneNumberUpdate


@pytest.fixture
def mock_db():
    return Mock(spec=Session)


@pytest.fixture
def number_service(mock_db):
    return NumberService(mock_db)


@pytest.fixture
def sample_phone_number():
    return PhoneNumber(
        id="test-id",
        twilio_sid="PN123456789",
        phone_number="+15551234567",
        friendly_name="Test Number",
        organization_id="org-123",
        user_id="user-123",
        country_code="US",
        number_type="local",
        capabilities=["voice", "sms"],
        status="active",
        monthly_price=1.15,
        total_calls=0,
        total_minutes=0.0,
        total_sms=0
    )


class TestNumberService:
    """Test cases for NumberService"""
    
    @pytest.mark.asyncio
    async def test_get_numbers_success(self, number_service, mock_db, sample_phone_number):
        """Test successful retrieval of phone numbers"""
        # Setup mock
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [sample_phone_number]
        
        mock_db.query.return_value = mock_query
        
        # Execute
        result = await number_service.get_numbers(
            organization_id="org-123",
            user_id="user-123"
        )
        
        # Assert
        assert result["total"] == 1
        assert len(result["numbers"]) == 1
        assert result["numbers"][0].phone_number == "+15551234567"
    
    @pytest.mark.asyncio
    async def test_update_number_success(self, number_service, mock_db, sample_phone_number):
        """Test successful phone number update"""
        # Setup mock
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_phone_number
        mock_db.query.return_value = mock_query
        
        # Mock Twilio service
        number_service.twilio.update_number_configuration = AsyncMock()
        
        # Execute
        update_data = PhoneNumberUpdate(friendly_name="Updated Name")
        result = await number_service.update_number("test-id", "org-123", update_data)
        
        # Assert
        assert result.friendly_name == "Updated Name"
        mock_db.commit.assert_called_once()


# apps/phone-numbers/tests/test_purchase_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

from services.purchase_service import PurchaseService
from schemas.phone_number import NumberPurchaseRequest


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def purchase_service(mock_db):
    return PurchaseService(mock_db)


@pytest.fixture
def sample_purchase_request():
    return NumberPurchaseRequest(
        phone_number="+15551234567",
        friendly_name="Test Purchase",
        number_type="local",
        capabilities=["voice", "sms"],
        payment_method_id="pm_test_123"
    )


class TestPurchaseService:
    """Test cases for PurchaseService"""
    
    @pytest.mark.asyncio
    @patch('stripe.PaymentIntent.create')
    async def test_initiate_purchase_success(
        self, 
        mock_stripe_create,
        purchase_service, 
        mock_db, 
        sample_purchase_request
    ):
        """Test successful purchase initiation"""
        # Setup mocks
        mock_stripe_create.return_value = {
            "id": "pi_test_123",
            "status": "succeeded",
            "customer": "cus_test_123"
        }
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        purchase_service._get_pricing = AsyncMock(return_value={
            "monthly_price": 1.15,
            "setup_fee": 0.0,
            "currency": "USD"
        })
        purchase_service._create_payment_intent = AsyncMock(return_value={
            "id": "pi_test_123",
            "status": "succeeded"
        })
        purchase_service._provision_number = AsyncMock()
        
        # Execute
        result = await purchase_service.initiate_purchase(
            organization_id="org-123",
            user_id="user-123",
            purchase_request=sample_purchase_request
        )
        
        # Assert
        assert result.phone_number == "+15551234567"
        assert result.status == "processing"
        mock_db.add.assert_called()
        mock_db.commit.assert_called()


# apps/phone-numbers/tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app

client = TestClient(app)


class TestNumberEndpoints:
    """Test cases for phone number endpoints"""
    
    @patch('api.v1.endpoints.numbers.get_current_user')
    @patch('api.v1.endpoints.numbers.get_organization_id')
    @patch('api.v1.endpoints.numbers.NumberService')
    def test_get_numbers_success(self, mock_service, mock_org_id, mock_user):
        """Test GET /api/v1/numbers endpoint"""
        # Setup mocks
        mock_user.return_value = {"id": "user-123"}
        mock_org_id.return_value = "org-123"
        
        mock_service_instance = Mock()
        mock_service_instance.get_numbers = AsyncMock(return_value={
            "numbers": [],
            "total": 0,
            "page": 1,
            "size": 100,
            "pages": 0
        })
        mock_service.return_value = mock_service_instance
        
        # Execute
        response = client.get(
            "/api/v1/numbers",
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "numbers" in data
        assert data["total"] == 0


# apps/phone-numbers/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from shared.database.client import get_db, Base


@pytest.fixture
def test_db():
    """Create test database"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create test client with test database"""
    def override_get_db():
        try:
            db = test_db()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {"Authorization": "Bearer test-token-123"}