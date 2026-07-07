import pytest
import responses
from requests.exceptions import ConnectionError

from n8n_client import N8nAPIError, N8nClient

BASE_URL = "http://localhost:5678"


@pytest.fixture
def client():
    return N8nClient(base_url=BASE_URL, api_key="test-key")


@responses.activate
def test_list_workflows(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows",
        json={"data": [{"id": "1", "name": "Wf 1"}]},
        status=200,
    )
    result = client.list_workflows()
    assert result == [{"id": "1", "name": "Wf 1"}]


@responses.activate
def test_create_workflow_sends_body(client):
    responses.add(
        responses.POST,
        f"{BASE_URL}/api/v1/workflows",
        json={"id": "42", "name": "New Workflow"},
        status=200,
    )
    result = client.create_workflow({"name": "New Workflow", "nodes": [], "connections": {}})
    assert result["id"] == "42"
    assert responses.calls[0].request.headers["X-N8N-API-KEY"] == "test-key"


@responses.activate
def test_activate_workflow(client):
    responses.add(
        responses.PATCH,
        f"{BASE_URL}/api/v1/workflows/42/activate",
        json={"id": "42", "active": True},
        status=200,
    )
    result = client.activate_workflow("42")
    assert result["active"] is True


@responses.activate
def test_delete_workflow_no_content(client):
    responses.add(
        responses.DELETE,
        f"{BASE_URL}/api/v1/workflows/42",
        body="",
        status=200,
    )
    assert client.delete_workflow("42") is None


@responses.activate
def test_get_workflow_executions(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows/42/executions",
        json={"data": [{"id": "run-1", "finished": True}]},
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": "5"})],
    )
    result = client.get_workflow_executions("42", limit=5)
    assert result == [{"id": "run-1", "finished": True}]


@responses.activate
def test_api_error_response_raises_n8n_api_error(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows/missing",
        json={"message": "Workflow not found"},
        status=404,
    )
    with pytest.raises(N8nAPIError, match="Workflow not found"):
        client.get_workflow("missing")


@responses.activate
def test_connection_error_raises_n8n_api_error(client):
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows",
        body=ConnectionError("refused"),
    )
    with pytest.raises(N8nAPIError, match="Could not connect"):
        client.list_workflows()
