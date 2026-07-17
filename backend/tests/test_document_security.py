import pytest
import io
from fastapi.testclient import TestClient
from main import app
from app.api.deps import get_current_user
from app.schemas.user import UserProfileResponse, RoleResponse

# Mock the dependency
async def override_get_current_user():
    return UserProfileResponse(
        id=1, 
        email="test@example.com", 
        name="Test User", 
        role=RoleResponse(id=1, name="user"), 
        is_active=True,
        is_verified=True
    )

@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

def test_upload_malicious_filename():
    file_content = b"fake payload"
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malicious.pdf", file_obj, "application/pdf")},
        data={"doc_type": "10-K"}
    )
    
    assert response.status_code == 400
    assert "malicious" in response.json()["detail"].lower()

def test_upload_exe_filename():
    file_content = b"fake payload"
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("virus.exe", file_obj, "application/x-msdownload")},
        data={"doc_type": "10-K"}
    )
    
    assert response.status_code == 400

def test_upload_file_size_limit():
    # Simulate a file larger than 50MB
    # TestClient doesn't easily let us send 51MB without blocking RAM,
    # but we can generate a large dummy bytes object.
    # To keep the test fast, let's assume we can mock or generate just enough.
    # Actually, generating 51MB in memory is quick for a test.
    file_content = b"0" * (50 * 1024 * 1024 + 1)
    file_obj = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("large.txt", file_obj, "text/plain")},
        data={"doc_type": "10-K"}
    )
    
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()
