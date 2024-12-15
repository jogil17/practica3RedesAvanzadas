import sys
import os
import pytest
from app import app


base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base_path)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
