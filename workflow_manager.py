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


@cli.command("list")
def list_workflows():
    """List all workflow files in workflows/ directory."""
    if not WORKFLOW_DIR.exists():
        click.echo(f"Workflow directory not found: {WORKFLOW_DIR}")
        return

    workflow_files = sorted(WORKFLOW_DIR.glob("*.json"))

    if not workflow_files:
        click.echo("No workflows found.")
        return

    click.echo(f"\nFound {len(workflow_files)} workflow(s):\n")

    for wf_file in workflow_files:
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
@click.option(
    "--dry-run", is_flag=True, help="Validate and preview the deploy without calling the n8n API"
)
def deploy(workflow_file: str, n8n_url: Optional[str], api_key: Optional[str], dry_run: bool):
    """Deploy a workflow to n8n instance."""
    filepath = Path(workflow_file)

    if not filepath.exists():
        click.echo(f"❌ File not found: {workflow_file}")
        return

    try:
        workflow_json = load_workflow_json(str(filepath))
        validate_n8n_json(workflow_json)
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        return

    if dry_run:
        click.echo(f"🔍 Dry run — would deploy: {workflow_json.get('name')}")
        click.echo(f"   Nodes: {len(workflow_json.get('nodes', []))}")
        click.echo(f"   Tags: {', '.join(workflow_json.get('tags', [])) or 'none'}")
        click.echo(f"   Active on deploy: {workflow_json.get('active', False)}")
        return

    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return

    try:
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


@cli.command()
@click.argument("workflow_id")
@click.option("--n8n-url", envvar="N8N_URL", help="n8n instance URL")
@click.option("--api-key", envvar="N8N_API_KEY", help="n8n API key")
def activate(workflow_id: str, n8n_url: Optional[str], api_key: Optional[str]):
    """Activate a workflow on the n8n instance."""
    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return

    try:
        client = N8nClient(base_url=n8n_url, api_key=api_key)
        result = client.activate_workflow(workflow_id)
        click.echo(f"✅ Activated: {result.get('name', workflow_id)}")
    except Exception as e:
        click.echo(f"❌ Activation failed: {e}")


@cli.command()
@click.argument("workflow_id")
@click.option("--n8n-url", envvar="N8N_URL", help="n8n instance URL")
@click.option("--api-key", envvar="N8N_API_KEY", help="n8n API key")
def deactivate(workflow_id: str, n8n_url: Optional[str], api_key: Optional[str]):
    """Deactivate a workflow on the n8n instance."""
    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return

    try:
        client = N8nClient(base_url=n8n_url, api_key=api_key)
        result = client.deactivate_workflow(workflow_id)
        click.echo(f"✅ Deactivated: {result.get('name', workflow_id)}")
    except Exception as e:
        click.echo(f"❌ Deactivation failed: {e}")


@cli.command()
@click.argument("workflow_id")
@click.option("--n8n-url", envvar="N8N_URL", help="n8n instance URL")
@click.option("--api-key", envvar="N8N_API_KEY", help="n8n API key")
@click.option("--limit", default=10, help="Maximum number of executions to show")
def executions(workflow_id: str, n8n_url: Optional[str], api_key: Optional[str], limit: int):
    """Show recent execution history for a workflow."""
    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return

    try:
        client = N8nClient(base_url=n8n_url, api_key=api_key)
        runs = client.get_workflow_executions(workflow_id, limit=limit)

        if not runs:
            click.echo("No executions found.")
            return

        click.echo(f"\nLast {len(runs)} execution(s):\n")
        for run in runs:
            status = "success" if run.get("finished") else run.get("status", "unknown")
            click.echo(f"  {run.get('id')}  {run.get('startedAt', '?')}  {status}")
    except Exception as e:
        click.echo(f"❌ Failed to fetch executions: {e}")


@cli.command()
@click.option("--n8n-url", envvar="N8N_URL", help="n8n instance URL")
@click.option("--api-key", envvar="N8N_API_KEY", help="n8n API key")
@click.option("--sample-size", default=5, help="Recent executions to sample per workflow")
def health(n8n_url: Optional[str], api_key: Optional[str], sample_size: int):
    """Check active/inactive status and recent execution success rate for all workflows."""
    if not n8n_url or not api_key:
        click.echo("❌ N8N_URL and N8N_API_KEY are required")
        click.echo("   Set them as environment variables or pass --n8n-url and --api-key")
        return

    try:
        client = N8nClient(base_url=n8n_url, api_key=api_key)
        remote_workflows = client.list_workflows()
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")
        return

    if not remote_workflows:
        click.echo("No workflows found on this n8n instance.")
        return

    active_count = sum(1 for wf in remote_workflows if wf.get("active"))
    click.echo(f"\n{len(remote_workflows)} workflow(s) — {active_count} active, "
               f"{len(remote_workflows) - active_count} inactive\n")

    for wf in remote_workflows:
        status_icon = "🟢" if wf.get("active") else "⚪"
        name = wf.get("name", "Unknown")
        workflow_id = wf.get("id")

        try:
            runs = client.get_workflow_executions(workflow_id, limit=sample_size)
        except Exception as e:
            click.echo(f"{status_icon} {name}  — could not fetch executions: {e}")
            continue

        if not runs:
            click.echo(f"{status_icon} {name}  — no executions yet")
            continue

        successes = sum(1 for run in runs if run.get("finished") and run.get("status") != "error")
        click.echo(f"{status_icon} {name}  — {successes}/{len(runs)} recent runs succeeded")


if __name__ == "__main__":
    cli()
