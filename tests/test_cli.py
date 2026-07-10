import responses
from click.testing import CliRunner

from workflow_manager import cli

BASE_URL = "http://localhost:5678"


def test_deploy_dry_run_does_not_call_api():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["deploy", "workflows/lead-routing-slack.json", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert "Lead Routing to Slack" in result.output


def test_deploy_dry_run_reports_validation_errors(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"name": "Bad"}')

    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", str(bad_file), "--dry-run"])
    assert "Validation failed" in result.output


@responses.activate
def test_health_reports_active_counts_and_success_rate():
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows",
        json={
            "data": [
                {"id": "1", "name": "Active Wf", "active": True},
                {"id": "2", "name": "Inactive Wf", "active": False},
            ]
        },
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows/1/executions",
        json={"data": [{"finished": True}, {"finished": False, "status": "error"}]},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE_URL}/api/v1/workflows/2/executions",
        json={"data": []},
        status=200,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["health", "--n8n-url", BASE_URL, "--api-key", "test-key"],
    )
    assert result.exit_code == 0
    assert "2 workflow(s) — 1 active, 1 inactive" in result.output
    assert "Active Wf  — 1/2 recent runs succeeded" in result.output
    assert "Inactive Wf  — no executions yet" in result.output


def test_health_requires_credentials():
    runner = CliRunner()
    result = runner.invoke(cli, ["health"], env={"N8N_URL": "", "N8N_API_KEY": ""})
    assert "N8N_URL and N8N_API_KEY are required" in result.output
