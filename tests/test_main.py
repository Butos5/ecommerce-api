from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_products_unauthorized():
    response = client.get("/products/")
    assert response.status_code == 401