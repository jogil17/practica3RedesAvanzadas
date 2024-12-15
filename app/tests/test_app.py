import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app.app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
