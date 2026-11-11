import pytest
import os
import json
import tempfile
import io
from unittest.mock import patch, MagicMock
from server import app
import server

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_atproto_did_route_configured(client, monkeypatch):
    monkeypatch.setenv('ATPROTO_DID', 'did:plc:test-did-123')
    response = client.get('/.well-known/atproto-did')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.data.decode('utf-8') == 'did:plc:test-did-123'

def test_atproto_did_route_default(client, monkeypatch):
    monkeypatch.delenv('ATPROTO_DID', raising=False)
    response = client.get('/.well-known/atproto-did')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert response.data.decode('utf-8') == 'did:plc:placeholder-agent-did'

def test_organization_details_no_api_key(client, monkeypatch):
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    response = client.post('/api/organization_details', json={'keywords': 'Test Agency'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "SAM.gov API key is not configured on the server."

@patch('server.requests.get')
def test_organization_details_success(mock_get, client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
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
def test_organization_details_not_found(mock_get, client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {"orglist": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.post('/api/organization_details', json={'keywords': 'Unknown Agency'})
    assert response.status_code == 404
    assert response.get_json()['error'] == "Organization not found."

def test_search_opportunities_missing_dates(client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    response = client.post('/api/search_opportunities', json={'keywords': 'Grant'})
    assert response.status_code == 400
    assert response.get_json()['error'] == "A date range is required."

@patch('server.requests.get')
def test_search_opportunities_success(mock_get, client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
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


@patch('server.requests.get')
@patch('server.requests.post')
def test_match_opportunities_job(mock_post, mock_get, client, monkeypatch):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({"researchProfile": {"capabilities": "AI", "topics": "ML"}, "matchedOpportunities": []}, tmp_file)
        tmp_file_name = tmp_file.name

    server.app.config['DATA_FILE'] = tmp_file_name
    monkeypatch.setenv("SAM_API_KEY", "fake-key")

    server.EXPERTS = {
        "Mock Expert": {
            "endpoint": "http://mock-llm.com/api",
            "api_key": "mock-key",
            "model_name": "mock-model"
        }
    }

    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {
        "opportunitiesData": [{
            "title": "Test Grant Opportunity",
            "noticeId": "12345"
        }]
    }
    mock_get_response.raise_for_status.return_value = None
    mock_get.return_value = mock_get_response

    mock_post_response = MagicMock()
    mock_post_response.json.return_value = {
        "choices": [{
            "message": {"content": '```json\n{"is_match": true, "justification": "Matches perfectly."}\n```'}
        }]
    }
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    server.match_opportunities_job()

    with open(tmp_file_name, 'r') as f:
        updated_data = json.load(f)

    assert len(updated_data["matchedOpportunities"]) == 1
    assert updated_data["matchedOpportunities"][0]["opportunity"]["title"] == "Test Grant Opportunity"
    assert updated_data["matchedOpportunities"][0]["match_analysis"]["is_match"] == True

    os.remove(tmp_file_name)

def test_load_data_with_missing_keys(client):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({}, tmp_file)
        tmp_file_name = tmp_file.name

    server.app.config['DATA_FILE'] = tmp_file_name

    response = client.get('/api/data')
    assert response.status_code == 200
    data = response.get_json()
    assert data["travelBudgets"] == []
    assert data["reportMetrics"]["status"] == "On Track"

    os.remove(tmp_file_name)

def test_save_data(client):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file_name = tmp_file.name

    server.app.config['DATA_FILE'] = tmp_file_name

    response = client.post('/api/data', json={"test": "data"})
    assert response.status_code == 200
    assert response.get_json()["success"] == True

    with open(tmp_file_name, 'r') as f:
        saved_data = json.load(f)

    assert saved_data == {"test": "data"}

    os.remove(tmp_file_name)

def test_search_psc_missing_keywords(client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    response = client.post('/api/psc', json={})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Keywords are required to search PSCs."

@patch('server.requests.get')
def test_search_psc_success(mock_get, client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "pscData": [{
            "pscCode": "R425",
            "pscName": "Engineering and Technical Services",
            "description": "Engineering services."
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.post('/api/psc', json={'keywords': 'Engineering'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["pscCode"] == "R425"

@patch('server.requests.get')
def test_search_psc_not_found(mock_get, client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {"pscData": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.post('/api/psc', json={'keywords': 'Unknown'})
    assert response.status_code == 200
    assert len(response.get_json()) == 0

def test_upload_file_no_file_part(client):
    response = client.post('/api/upload', data={})
    assert response.status_code == 400
    assert response.get_json()['error'] == "No file part."

def test_upload_file_no_selected_file(client):
    data = {'file': (io.BytesIO(b""), '')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['error'] == "No selected file."

def test_upload_file_not_allowed(client):
    data = {'file': (io.BytesIO(b"malicious code"), 'test.exe')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['error'] == "File type not allowed."

def test_upload_file_success(client):
    data = {'file': (io.BytesIO(b"test file content"), 'test.txt')}
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['success'] is True
    assert json_data['filename'] == 'test.txt'
    assert 'path' in json_data

def test_serve_upload(client):
    data = {'file': (io.BytesIO(b"test file content"), 'serve_test.txt')}
    client.post('/api/upload', data=data, content_type='multipart/form-data')

    response = client.get('/uploads/serve_test.txt')
    assert response.status_code == 200
    assert response.data == b"test file content"

@patch('server.requests.post')
def test_chat_handler_success(mock_post, client):
    server.EXPERTS = {
        "TestExpert": {
            "endpoint": "http://test.com",
            "api_key": "test_key",
            "model_name": "test_model"
        }
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {"reply": "hello"}
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    response = client.post('/api/chat', json={"model": "TestExpert", "messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 200
    assert response.get_json() == {"reply": "hello"}

def test_chat_handler_invalid_request(client):
    response = client.post('/api/chat', json={"wrong_key": "val"})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid request body."

def test_chat_handler_expert_not_found(client):
    server.EXPERTS = {}
    response = client.post('/api/chat', json={"model": "NonExistent", "messages": []})
    assert response.status_code == 404
    assert response.get_json()['error'] == "Expert 'NonExistent' not found."

def test_gsa_perdiem_dc(client):
    response = client.get('/api/gsa_perdiem?destination=washington dc')
    assert response.status_code == 200
    data = response.get_json()
    assert data["lodging"] == 258
    assert data["meals"] == 79

def test_gsa_perdiem_ny(client):
    response = client.get('/api/gsa_perdiem?destination=new york')
    assert response.status_code == 200
    data = response.get_json()
    assert data["lodging"] == 286
    assert data["meals"] == 79

def test_gsa_perdiem_ca(client):
    response = client.get('/api/gsa_perdiem?destination=los angeles, ca')
    assert response.status_code == 200
    data = response.get_json()
    assert data["lodging"] == 270
    assert data["meals"] == 74

def test_gsa_perdiem_default(client):
    response = client.get('/api/gsa_perdiem?destination=unknown')
    assert response.status_code == 200
    data = response.get_json()
    assert data["lodging"] == 107
    assert data["meals"] == 59

def test_load_experts_from_env(monkeypatch):
    monkeypatch.setenv("LLM_1_NAME", "EnvExpert")
    monkeypatch.setenv("LLM_1_ENDPOINT", "http://env.com")
    monkeypatch.setenv("LLM_1_KEY", "env_key")

    server.load_experts_from_env()
    assert "EnvExpert" in server.EXPERTS
    assert server.EXPERTS["EnvExpert"]["endpoint"] == "http://env.com"
    assert server.EXPERTS["EnvExpert"]["api_key"] == "env_key"
    assert server.EXPERTS["EnvExpert"]["model_name"] == "EnvExpert"

def test_get_experts(client):
    server.EXPERTS = {"Exp1": {}, "Exp2": {}}
    response = client.get('/api/experts')
    assert response.status_code == 200
    assert set(response.get_json()) == {"Exp1", "Exp2"}

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

@patch('server.requests.get')
def test_organization_details_request_exception(mock_get, client, monkeypatch):
    import requests
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_get.side_effect = requests.exceptions.RequestException("API down")
    response = client.post('/api/organization_details', json={'keywords': 'Test Agency'})
    assert response.status_code == 502
    assert "Failed to connect" in response.get_json()['error']

def test_organization_details_missing_keywords(client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    response = client.post('/api/organization_details', json={})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Organization name (keywords) is required."

@patch('server.requests.get')
def test_search_opportunities_request_exception(mock_get, client, monkeypatch):
    import requests
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_get.side_effect = requests.exceptions.RequestException("API down")
    response = client.post('/api/search_opportunities', json={
        'keywords': 'Grant', 'postedFrom': '2024-01-01', 'postedTo': '2024-12-31'
    })
    assert response.status_code == 502
    assert "Failed to connect" in response.get_json()['error']

@patch('server.requests.get')
def test_search_psc_request_exception(mock_get, client, monkeypatch):
    import requests
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_get.side_effect = requests.exceptions.RequestException("API down")
    response = client.post('/api/psc', json={'keywords': 'Engineering'})
    assert response.status_code == 502
    assert "Failed to connect" in response.get_json()['error']

@patch('server.requests.post')
def test_chat_handler_request_exception(mock_post, client):
    import requests
    server.EXPERTS = {"TestExpert": {"endpoint": "http://test.com", "api_key": "test_key", "model_name": "test_model"}}
    mock_post.side_effect = requests.exceptions.RequestException("LLM API down")
    response = client.post('/api/chat', json={"model": "TestExpert", "messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 502
    assert "Failed to connect" in response.get_json()['error']

def test_chat_handler_unexpected_exception(client, monkeypatch):
    server.EXPERTS = {"TestExpert": {"endpoint": "http://test.com", "api_key": "test_key", "model_name": "test_model"}}
    def raise_err(*args, **kwargs):
        raise ValueError("Unexpected!")
    monkeypatch.setattr('server.requests.post', raise_err)
    response = client.post('/api/chat', json={"model": "TestExpert", "messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 500
    assert response.get_json()['error'] == "An unexpected error occurred."

def test_draft_application_invalid_request(client):
    response = client.post('/api/draft_application', json={})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid request body."

def test_draft_application_expert_not_found(client):
    server.EXPERTS = {}
    response = client.post('/api/draft_application', json={
        'opportunity': {'title': 'AI Grant'}, 'profile': {'capabilities': 'AI'}, 'expert': 'Missing'
    })
    assert response.status_code == 404
    assert response.get_json()['error'] == "Expert 'Missing' not found."

@patch('server.requests.post')
def test_draft_application_request_exception(mock_post, client):
    import requests
    server.EXPERTS = {"TestExpert": {"endpoint": "http://test.com", "api_key": "test_key", "model_name": "test_model"}}
    mock_post.side_effect = requests.exceptions.RequestException("LLM API down")
    response = client.post('/api/draft_application', json={
        'opportunity': {'title': 'AI Grant'}, 'profile': {'capabilities': 'AI'}, 'expert': 'TestExpert'
    })
    assert response.status_code == 502
    assert "Failed to connect" in response.get_json()['error']

def test_draft_application_unexpected_exception(client, monkeypatch):
    server.EXPERTS = {"TestExpert": {"endpoint": "http://test.com", "api_key": "test_key", "model_name": "test_model"}}
    def raise_err(*args, **kwargs):
        raise ValueError("Unexpected!")
    monkeypatch.setattr('server.requests.post', raise_err)
    response = client.post('/api/draft_application', json={
        'opportunity': {'title': 'AI Grant'}, 'profile': {'capabilities': 'AI'}, 'expert': 'TestExpert'
    })
    assert response.status_code == 500
    assert "unexpected error" in response.get_json()['error']

def assert_prompt_contains(mock_post, expected_substring):
    args, kwargs = mock_post.call_args
    prompt = kwargs['json']['messages'][0]['content']
    assert expected_substring in prompt, f"Expected '{expected_substring}' in prompt, got:\n{prompt}"

@patch('server.requests.post')
def test_draft_application_org_types(mock_post, client):
    server.EXPERTS = {"TestExpert": {"endpoint": "http://test.com", "api_key": "k", "model_name": "m"}}
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "draft"}}]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    base_payload = {'opportunity': {'title': 'T'}, 'expert': 'TestExpert'}

    client.post('/api/draft_application', json={**base_payload, 'profile': {'organizationType': 'For-Profit'}})
    assert_prompt_contains(mock_post, "return on investment (ROI)")

    client.post('/api/draft_application', json={**base_payload, 'profile': {'organizationType': 'Academic Institution'}})
    assert_prompt_contains(mock_post, "educational impact")

    client.post('/api/draft_application', json={**base_payload, 'profile': {'organizationType': 'NGO'}})
    assert_prompt_contains(mock_post, "sustainable development")

    client.post('/api/draft_application', json={**base_payload, 'profile': {'organizationType': 'Individual/Researcher'}})
    assert_prompt_contains(mock_post, "personal expertise")

    client.post('/api/draft_application', json={**base_payload, 'profile': {'organizationType': 'CustomType'}})
    assert_prompt_contains(mock_post, "Tailor the proposal for a CustomType entity")

@patch('server.requests.post')
def test_draft_application_proposal_types(mock_post, client):
    server.EXPERTS = {"TestExpert": {"endpoint": "http://test.com", "api_key": "k", "model_name": "m"}}
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "draft"}}]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    base_payload = {'opportunity': {'title': 'T'}, 'profile': {'capabilities': 'C'}, 'expert': 'TestExpert'}

    client.post('/api/draft_application', json={**base_payload, 'proposalType': 'OTA/Milestone-Driven'})
    assert_prompt_contains(mock_post, "Milestone-Driven Execution")

    client.post('/api/draft_application', json={**base_payload, 'proposalType': 'Mini-study (OSDR Praxis)', 'profile': {'osdrDataReviewType': 'DRT', 'osdrContext': 'CTX'}})
    assert_prompt_contains(mock_post, "OSDR Praxis mini-study")
    assert_prompt_contains(mock_post, "DRT")
    assert_prompt_contains(mock_post, "CTX")

def test_match_opportunities_job_missing_data_file(monkeypatch, capsys):
    monkeypatch.setattr(server.app.config, 'get', lambda k: "missing.json" if k == "DATA_FILE" else None)
    server.match_opportunities_job()
    captured = capsys.readouterr()
    assert "Data file not found" in captured.out

def test_match_opportunities_job_empty_profile(client, capsys):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({"researchProfile": {}}, tmp_file)
        tmp_file_name = tmp_file.name
    server.app.config['DATA_FILE'] = tmp_file_name
    server.match_opportunities_job()
    captured = capsys.readouterr()
    assert "Research profile is empty" in captured.out
    os.remove(tmp_file_name)

def test_match_opportunities_job_no_api_key(client, capsys, monkeypatch):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({"researchProfile": {"capabilities": "A", "topics": "B"}}, tmp_file)
        tmp_file_name = tmp_file.name
    server.app.config['DATA_FILE'] = tmp_file_name
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    server.match_opportunities_job()
    captured = capsys.readouterr()
    assert "SAM.gov API key not configured" in captured.out
    os.remove(tmp_file_name)

@patch('server.requests.get')
def test_match_opportunities_job_sam_exception(mock_get, client, capsys, monkeypatch):
    import requests
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({"researchProfile": {"capabilities": "A", "topics": "B"}}, tmp_file)
        tmp_file_name = tmp_file.name
    server.app.config['DATA_FILE'] = tmp_file_name
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_get.side_effect = requests.exceptions.RequestException("API down")
    server.match_opportunities_job()
    captured = capsys.readouterr()
    assert "Error calling SAM.gov API" in captured.out
    os.remove(tmp_file_name)

@patch('server.requests.get')
def test_match_opportunities_job_no_experts(mock_get, client, capsys, monkeypatch):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({"researchProfile": {"capabilities": "A", "topics": "B"}}, tmp_file)
        tmp_file_name = tmp_file.name
    server.app.config['DATA_FILE'] = tmp_file_name
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {"opportunitiesData": [{"title": "opp"}]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    server.EXPERTS = {}
    server.match_opportunities_job()
    captured = capsys.readouterr()
    assert "No LLM experts configured for matching" in captured.out
    os.remove(tmp_file_name)

@patch('server.requests.get')
@patch('server.requests.post')
def test_match_opportunities_job_llm_exception(mock_post, mock_get, client, capsys, monkeypatch):
    import requests
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        json.dump({"researchProfile": {"capabilities": "A", "topics": "B"}}, tmp_file)
        tmp_file_name = tmp_file.name
    server.app.config['DATA_FILE'] = tmp_file_name
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = {"opportunitiesData": [{"title": "opp", "noticeId": "123"}]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    server.EXPERTS = {"Exp": {"endpoint": "e", "api_key": "k", "model_name": "m"}}
    mock_post.side_effect = requests.exceptions.RequestException("LLM fail")
    server.match_opportunities_job()
    captured = capsys.readouterr()
    assert "Error analyzing opportunity" in captured.out
    os.remove(tmp_file_name)

def test_load_experts_no_experts(capsys, monkeypatch):
    keys_to_delete = [k for k in os.environ if k.startswith("LLM_")]
    for k in keys_to_delete:
        monkeypatch.delenv(k, raising=False)
    server.load_experts_from_env()
    captured = capsys.readouterr()
    assert "Warning: No LLM experts configured" in captured.out

def test_load_data_exception(client, monkeypatch):
    monkeypatch.setattr(server.os.path, 'exists', lambda p: True)
    def mock_open(*args, **kwargs):
        raise IOError("Cannot open file")
    monkeypatch.setattr('builtins.open', mock_open)
    response = client.get('/api/data')
    assert response.status_code == 500
    assert response.get_json()['error'] == "Could not load data."

def test_save_data_exception(client, monkeypatch):
    def mock_open(*args, **kwargs):
        raise IOError("Cannot save file")
    monkeypatch.setattr('builtins.open', mock_open)
    response = client.post('/api/data', json={})
    assert response.status_code == 500
    assert response.get_json()['error'] == "Could not save data."

def test_organization_details_unexpected_exception(client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    def raise_err(*args, **kwargs):
        raise ValueError("Unexpected")
    monkeypatch.setattr('server.requests.get', raise_err)
    response = client.post('/api/organization_details', json={'keywords': 'A'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "An unexpected error occurred."

def test_search_opportunities_unexpected_exception(client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    def raise_err(*args, **kwargs):
        raise ValueError("Unexpected")
    monkeypatch.setattr('server.requests.get', raise_err)
    response = client.post('/api/search_opportunities', json={'keywords': 'A', 'postedFrom': 'x', 'postedTo': 'y'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "An unexpected error occurred."

def test_search_psc_unexpected_exception(client, monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "fake-key")
    def raise_err(*args, **kwargs):
        raise ValueError("Unexpected")
    monkeypatch.setattr('server.requests.get', raise_err)
    response = client.post('/api/psc', json={'keywords': 'A'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "An unexpected error occurred."

def test_search_psc_no_api_key(client, monkeypatch):
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    response = client.post('/api/psc', json={'keywords': 'A'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "SAM.gov API key is not configured on the server."

def test_search_opportunities_no_api_key(client, monkeypatch):
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    response = client.post('/api/search_opportunities', json={'keywords': 'A', 'postedFrom': 'x', 'postedTo': 'y'})
    assert response.status_code == 500
    assert response.get_json()['error'] == "SAM.gov API key is not configured on the server."
