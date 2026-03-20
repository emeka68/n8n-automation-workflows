#!/usr/bin/env python3
"""
n8n Workflow Manager CLI

CLI tool for managing n8n workflows: list, validate, deploy, backup.
"""

import os
import json
import click
from pathlib import Path
from typing import Optional
import jsonschema

from n8n_client import N8nClient


WORKFLOW_DIR = Path(__file__).parent / "workflows"


def load_workflow_json(filepath: str) -> dict:
    """Load workflow JSON from file."""
    with open(filepath, "r") as f:
        return json.load(f)


def validate_n8n_json(workflow_json: dict) -> bool:
    """
    Validate n8n workflow JSON schema.
    
    Basic validation - checks for required fields.
    """
    required_fields = ["name", "nodes", "connections"]
    
    for field in required_fields:
        if field not in workflow_json:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(workflow_json["nodes"], list):
        raise ValueError("'nodes' must be a list")
    
    if not isinstance(workflow_json["connections"], dict):
        raise ValueError("'connections' must be a dict")
    
    for node in workflow_json["nodes"]:
        if "name" not in node or "type" not in node:
            raise ValueError("Each node must have 'name' and 'type' fields")
    
    return True


@click.group()
def cli():
    """n8n Workflow Manager - CLI tool for workflow management."""
    pass


@cli.command()
def list():
    """List all workflow files in workflows/ directory."""
    if not WORKFLOW_DIR.exists():
        click.echo(f"Workflow directory not found: {WORKFLOW_DIR}")
        return
    
    workflows = list(WORKFLOW_DIR.glob("*.json"))
    
    if not workflows:
        click.echo("No workflows found.")
        return
    
    click.echo(f"\nFound {len(workflows)} workflow(s):\n")
    
    for wf_file in sorted(workflows):
        try:
            wf_json = load_workflow_json(str(wf_file))
            name = wf_json.get("name", "Unknown")
            desc = wf_json.get("description", "No description")
            nodes_count = len(wf_json.get("nodes", []))
            tags = ", ".join(wf_json.get("tags", []))
            
            click.echo(f"📋 {wf_file.name}")
            click.echo(f"   Name: {name}")
            click.echo(f"   Description: {desc}")
            click.echo(f"   Nodes: {nodes_count}")
            click.echo(f"   Tags: {tags or 'none'}")
            click.echo()
        except Exception as e:
            click.echo(f"❌ Error reading {wf_file.name}: {e}")
            click.echo()


@cli.command()
@click.argument("workflow_file")
def validate(workflow_file: str):
    """Validate a workflow JSON file."""
    filepath = Path(workflow_file)
    
    if not filepath.exists():
        click.echo(f"❌ File not found: {workflow_file}")
        return
    
    try:
        workflow_json = load_workflow_json(str(filepath))
        validate_n8n_json(workflow_json)
        click.echo(f"✅ {filepath.name} is valid n8n workflow JSON")
        click.echo(f"   Name: {workflow_json.get('name')}")
        click.echo(f"   Nodes: {len(workflow_json.get('nodes', []))}")
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")


@cli.command()
@click.argument("workflow_file")
@click.option("--n8n-url", envvar="N8N_URL", help="n8n instance URL")
@click.option("--api-key", envvar="N8N_API_KEY", help="n8n API key")
def deploy(workflow_file: str, n8n_url: Optional[str], api_key: Optional[str]):
    """Deploy a workflow to n8n instance."""
    filepath = Path(workflow_file)
    
    if not filepath.exists():
        click.echo(f"❌ File not found: {workflow_file}")
        return
    
    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return
    
    try:
        workflow_json = load_workflow_json(str(filepath))
        validate_n8n_json(workflow_json)
        
        client = N8nClient(base_url=n8n_url, api_key=api_key)
        result = client.create_workflow(workflow_json)
        
        workflow_id = result.get("id")
        click.echo(f"✅ Deployed: {workflow_json.get('name')}")
        click.echo(f"   Workflow ID: {workflow_id}")
    except Exception as e:
        click.echo(f"❌ Deployment failed: {e}")


@cli.command()
@click.option("--n8n-url", envvar="N8N_URL", help="n8n instance URL")
@click.option("--api-key", envvar="N8N_API_KEY", help="n8n API key")
@click.option("--output", "-o", default="backup.json", help="Output file for backup")
def backup(n8n_url: Optional[str], api_key: Optional[str], output: str):
    """Backup all workflows from n8n instance to local JSON file."""
    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return
    
    try:
        client = N8nClient(base_url=n8n_url, api_key=api_key)
        workflows = client.list_workflows()
        
        backup_data = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "workflows": workflows,
        }
        
        with open(output, "w") as f:
            json.dump(backup_data, f, indent=2)
        
        click.echo(f"✅ Backed up {len(workflows)} workflow(s) to {output}")
    except Exception as e:
        click.echo(f"❌ Backup failed: {e}")


if __name__ == "__main__":
    cli()
