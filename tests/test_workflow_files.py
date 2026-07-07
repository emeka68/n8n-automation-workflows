"""Validate every checked-in workflow JSON file against the n8n schema check."""

import json
from pathlib import Path

import pytest

from workflow_manager import validate_n8n_json

WORKFLOW_DIR = Path(__file__).parent.parent / "workflows"
WORKFLOW_FILES = sorted(WORKFLOW_DIR.glob("*.json"))


@pytest.mark.parametrize("workflow_file", WORKFLOW_FILES, ids=lambda p: p.name)
def test_workflow_file_is_valid(workflow_file):
    with open(workflow_file) as f:
        workflow_json = json.load(f)

    assert validate_n8n_json(workflow_json) is True


@pytest.mark.parametrize("workflow_file", WORKFLOW_FILES, ids=lambda p: p.name)
def test_workflow_file_has_metadata(workflow_file):
    with open(workflow_file) as f:
        workflow_json = json.load(f)

    assert workflow_json.get("name")
    assert workflow_json.get("nodes")


def test_at_least_six_workflows_present():
    assert len(WORKFLOW_FILES) == 6
