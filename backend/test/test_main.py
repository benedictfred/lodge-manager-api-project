from fastapi.testclient import TestClient
import app.main
from fastapi import status

from app.core.config import settings

client = TestClient(app.main.app)

def test_return_health_check():
    """
    Tests the health check endpoint to ensure the API is running and returns a 200 status code.
    """
    response = client.get('/healthy')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Your {settings.PROJECT_NAME} is working well"}