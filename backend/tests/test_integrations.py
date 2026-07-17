import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.integrations.engine import IntegrationEngine
from app.models.integration import IntegrationProvider, ConnectedAccount, CredentialVault
from app.integrations.auth import CredentialManager
from main import app

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.mark.asyncio
async def test_credential_vault_encryption(mock_db):
    auth = CredentialManager(mock_db)
    payload = {"api_key": "test_secret_123"}
    
    # Test encryption
    encrypted = auth.encrypt(payload)
    assert encrypted != '{"api_key": "test_secret_123"}'
    
    # Test decryption
    decrypted = auth.decrypt(encrypted)
    assert decrypted["api_key"] == "test_secret_123"

@pytest.mark.asyncio
async def test_connect_provider(mock_db):
    engine = IntegrationEngine(mock_db)
    
    # Mock provider from DB
    provider_model = IntegrationProvider(id=1, name="mock_bank")
    class MockResult:
        def scalar_one_or_none(self): return provider_model
        def scalars(self):
            class S:
                def all(self): return [provider_model]
            return S()
            
    mock_db.execute.return_value = MockResult()
    
    # Valid Connection
    account = await engine.connect_provider(
        user_id=1, 
        provider_name="mock_bank", 
        credentials={"api_key": "valid_key"}
    )
    assert account.user_id == 1
    assert account.provider_id == 1
    assert "bank_acct_" in account.external_account_id

    # Invalid connection
    with pytest.raises(Exception):
        await engine.connect_provider(
            user_id=1,
            provider_name="mock_bank",
            credentials={"api_key": "invalid"}
        )

@pytest.mark.asyncio
async def test_import_engine(mock_db):
    from app.integrations.import_engine import ImportEngine
    importer = ImportEngine(mock_db)
    
    # Test CSV parsing
    csv_content = "date,amount,desc\n2023-10-01,10.50,Coffee\n2023-10-02,-1500,Payroll\n"
    records = await importer.parse_csv(csv_content)
    assert len(records) == 2
    assert records[0]["amount"] == "10.50"
    
    # Test JSON parsing
    json_content = '[{"date": "2023-10-01", "amount": 10.50}]'
    records = await importer.parse_json(json_content)
    assert len(records) == 1
    assert records[0]["amount"] == 10.50

@pytest.mark.asyncio
async def test_export_engine(mock_db):
    from app.integrations.export_engine import ExportEngine
    exporter = ExportEngine(mock_db)
    
    data = [{"id": 1, "value": "test1"}, {"id": 2, "value": "test2"}]
    
    csv_output = await exporter.generate_csv(data)
    assert "id,value" in csv_output
    assert "1,test1" in csv_output
    
    json_output = await exporter.generate_json(data)
    assert '"id": 1' in json_output

def test_api_routes():
    from app.api.auth import get_current_user
    from app.models.user import User
    app.dependency_overrides[get_current_user] = lambda: User(id=1)
    client = TestClient(app)
    
    with patch("app.integrations.engine.IntegrationEngine.get_health", new_callable=AsyncMock) as mh:
        mh.return_value = {"mock_bank": "ok", "mock_broker": "ok"}
        res = client.get("/api/v1/integrations/health")
        assert res.status_code == 200
        assert res.json()["mock_bank"] == "ok"
    
    app.dependency_overrides.clear()
