from workflow_manager import validate_n8n_json
from workflow_templates import (
    create_alert_to_ticket,
    create_scheduled_report,
    create_webhook_to_slack,
)


def test_create_webhook_to_slack_is_valid_and_substitutes_params():
    wf = create_webhook_to_slack(
        webhook_path="/webhook/alerts",
        slack_channel="#alerts",
        message_template="Alert: {{ $json.message }}",
    )
    assert validate_n8n_json(wf) is True
    assert wf["name"] == "Webhook to #alerts"

    webhook_node = next(n for n in wf["nodes"] if n["name"] == "Webhook")
    slack_node = next(n for n in wf["nodes"] if n["name"] == "Slack")
    assert webhook_node["parameters"]["path"] == "/webhook/alerts"
    assert slack_node["parameters"]["channel"] == "#alerts"
    assert slack_node["parameters"]["text"] == "Alert: {{ $json.message }}"
    assert wf["connections"]["Webhook"]["main"][0][0]["node"] == "Slack"


def test_create_scheduled_report_is_valid_and_substitutes_params():
    wf = create_scheduled_report(
        cron_expression="0 9 * * 1",
        data_source_url="https://api.example.com/metrics",
        report_recipients=["a@example.com", "b@example.com"],
    )
    assert validate_n8n_json(wf) is True

    fetch_node = next(n for n in wf["nodes"] if n["name"] == "Fetch Data")
    email_node = next(n for n in wf["nodes"] if n["name"] == "Email")
    assert fetch_node["parameters"]["url"] == "https://api.example.com/metrics"
    assert "a@example.com" in email_node["parameters"]["to"]
    assert "b@example.com" in email_node["parameters"]["to"]


def test_create_alert_to_ticket_is_valid_and_substitutes_params():
    wf = create_alert_to_ticket(
        alert_webhook="/webhook/pagerduty",
        jira_project="OPS",
        slack_channel="#incidents",
    )
    assert validate_n8n_json(wf) is True

    webhook_node = next(n for n in wf["nodes"] if n["name"] == "Alert Webhook")
    jira_node = next(n for n in wf["nodes"] if n["name"] == "Create Jira")
    slack_node = next(n for n in wf["nodes"] if n["name"] == "Notify Slack")
    assert webhook_node["parameters"]["path"] == "/webhook/pagerduty"
    assert jira_node["parameters"]["project"] == "OPS"
    assert slack_node["parameters"]["channel"] == "#incidents"
