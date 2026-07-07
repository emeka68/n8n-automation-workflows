import pytest

from workflow_manager import validate_n8n_json


def test_valid_minimal_workflow():
    workflow = {
        "name": "Minimal",
        "nodes": [{"name": "Start", "type": "n8n-nodes-base.start"}],
        "connections": {},
    }
    assert validate_n8n_json(workflow) is True


@pytest.mark.parametrize("missing_field", ["name", "nodes", "connections"])
def test_missing_required_field_raises(missing_field):
    workflow = {
        "name": "Minimal",
        "nodes": [{"name": "Start", "type": "n8n-nodes-base.start"}],
        "connections": {},
    }
    del workflow[missing_field]

    with pytest.raises(ValueError, match=f"Missing required field: {missing_field}"):
        validate_n8n_json(workflow)


def test_nodes_must_be_a_list():
    workflow = {"name": "Bad", "nodes": {}, "connections": {}}
    with pytest.raises(ValueError, match="'nodes' must be a list"):
        validate_n8n_json(workflow)


def test_connections_must_be_a_dict():
    workflow = {"name": "Bad", "nodes": [], "connections": []}
    with pytest.raises(ValueError, match="'connections' must be a dict"):
        validate_n8n_json(workflow)


def test_node_missing_name_or_type_raises():
    workflow = {
        "name": "Bad",
        "nodes": [{"type": "n8n-nodes-base.start"}],
        "connections": {},
    }
    with pytest.raises(ValueError, match="Each node must have 'name' and 'type' fields"):
        validate_n8n_json(workflow)
