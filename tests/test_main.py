import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import app
import pytest
from fastapi.testclient import TestClient
from jose import jwt

client = TestClient(app)
SECRET_KEY = "your-secret-key"  # Must match src/main.py
ALGORITHM = "HS256"

def create_test_token(username: str = "admin"):
    payload = {"sub": username}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def test_get_products():
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/products/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)