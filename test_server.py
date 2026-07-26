import pytest
import os
import json
from unittest.mock import patch, MagicMock
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_atproto_did_route_configured(client):
    os.environ['ATPROTO_DID'] = 'did:plc:test-did-123'
    response = client.get('/.well-known/atproto-did')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.data.decode('utf-8') == 'did:plc:test-did-123'

def test_atproto_did_route_default(client):
    if 'ATPROTO_DID' in os.environ:
        del os.environ['ATPROTO_DID']
    response = client.get('/.well-known/atproto-did')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.data.decode('utf-8') == 'did:plc:placeholder-agent-did'

def test_organization_details_no_api_key(client):
    if "SAM_API_KEY" in os.environ:
        del os.environ["SAM_API_KEY"]
    response = client.post('/api/organization_details', json={'keywords': 'Test Agency'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "SAM.gov API key is not configured on the server."

@patch('server.requests.get')
def test_organization_details_success(mock_get, client):
    os.environ["SAM_API_KEY"] = "fake-key"
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "orglist": [{
            "fhorgname": "Test Agency",
            "fhorgtype": "Department/Ind. Agency",
            "status": "ACTIVE",
            "description": "A mock agency.",
            "links": []
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.post('/api/organization_details', json={'keywords': 'Test Agency'})
    assert response.status_code == 200
    data = response.get_json()
    assert data["fhorgname"] == "Test Agency"
    assert data["status"] == "ACTIVE"

@patch('server.requests.get')
def test_organization_details_not_found(mock_get, client):
    os.environ["SAM_API_KEY"] = "fake-key"
    mock_response = MagicMock()
    mock_response.json.return_value = {"orglist": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.post('/api/organization_details', json={'keywords': 'Unknown Agency'})
    assert response.status_code == 404
    assert response.get_json()['error'] == "Organization not found."

def test_search_opportunities_missing_dates(client):
    os.environ["SAM_API_KEY"] = "fake-key"
    response = client.post('/api/search_opportunities', json={'keywords': 'Grant'})
    assert response.status_code == 400
    assert response.get_json()['error'] == "A date range is required."

@patch('server.requests.get')
def test_search_opportunities_success(mock_get, client):
    os.environ["SAM_API_KEY"] = "fake-key"
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "opportunitiesData": [{
            "title": "Test Grant Opportunity",
            "fullParentPathName": "Test Agency"
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.post('/api/search_opportunities', json={
        'keywords': 'Grant',
        'postedFrom': '2024-01-01',
        'postedTo': '2024-12-31'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Grant Opportunity"

@patch('server.requests.post')
def test_draft_application(mock_post, client, monkeypatch):
    import server
    server.EXPERTS = {
        "Mock Expert": {
            "endpoint": "http://mock-llm.com/api",
            "api_key": "mock-key",
            "model_name": "mock-model"
        }
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {"content": "Here is your application draft."}
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    response = client.post('/api/draft_application', json={
        'opportunity': {'title': 'AI Grant'},
        'profile': {'capabilities': 'AI and ML'},
        'expert': 'Mock Expert'
    })

    assert response.status_code == 200
    assert response.get_json()["draft"] == "Here is your application draft."
