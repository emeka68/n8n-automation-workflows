"""
Workflow Template Generators

Programmatically generate n8n workflow JSON for common use cases.
"""

import json
from typing import Dict, List, Any, Optional


def create_webhook_to_slack(
    webhook_path: str, slack_channel: str, message_template: str
) -> Dict[str, Any]:
    """
    Generate a webhook → Slack notification workflow.
    
    Args:
        webhook_path: Webhook path (e.g., "/webhook/alerts")
        slack_channel: Slack channel name (e.g., "#alerts")
        message_template: Message template with {{ }} placeholders
        
    Returns:
        n8n workflow JSON dict
    """
    return {
        "name": f"Webhook to {slack_channel}",
        "description": f"Sends webhook data to {slack_channel} Slack channel",
        "nodes": [
            {
                "parameters": {
                    "path": webhook_path,
                    "responseMode": "onReceived",
                    "options": {},
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300],
            },
            {
                "parameters": {
                    "authentication": "oAuth2",
                    "channel": slack_channel,
                    "messageType": "text",
                    "text": message_template,
                },
                "name": "Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 2,
                "position": [450, 300],
            },
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [{"node": "Slack", "type": "main", "index": 0}]
                ]
            }
        },
        "active": False,
        "settings": {
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
        },
        "tags": ["webhook", "slack"],
    }


def create_scheduled_report(
    cron_expression: str, data_source_url: str, report_recipients: List[str]
) -> Dict[str, Any]:
    """
    Generate a scheduled report workflow.
    
    Args:
        cron_expression: Cron schedule (e.g., "0 9 * * 1" for 9am Mondays)
        data_source_url: API endpoint to fetch data from
        report_recipients: List of email addresses
        
    Returns:
        n8n workflow JSON dict
    """
    recipients_json = json.dumps(report_recipients)
    
    return {
        "name": "Scheduled Report",
        "description": f"Scheduled report from {data_source_url}",
        "nodes": [
            {
                "parameters": {
                    "triggerTz": "America/New_York",
                    "rule": {"interval": [{"field": "minutes", "value": 1}]},
                },
                "name": "Schedule",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.1,
                "position": [250, 300],
            },
            {
                "parameters": {
                    "url": data_source_url,
                    "method": "GET",
                    "authentication": "apiKey",
                },
                "name": "Fetch Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [450, 300],
            },
            {
                "parameters": {
                    "authentication": "oAuth2",
                    "to": recipients_json,
                    "subject": "Daily Report",
                    "emailType": "html",
                    "htmlBody": "<h2>Report</h2><p>{{ JSON.stringify($json) }}</p>",
                },
                "name": "Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [650, 300],
            },
        ],
        "connections": {
            "Schedule": {
                "main": [
                    [{"node": "Fetch Data", "type": "main", "index": 0}]
                ]
            },
            "Fetch Data": {
                "main": [
                    [{"node": "Email", "type": "main", "index": 0}]
                ]
            },
        },
        "active": False,
        "settings": {
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
        },
        "tags": ["scheduled", "reporting"],
    }


def create_alert_to_ticket(
    alert_webhook: str, jira_project: str, slack_channel: str
) -> Dict[str, Any]:
    """
    Generate an alert → Jira ticket workflow.
    
    Args:
        alert_webhook: Webhook path for alerts
        jira_project: Jira project key
        slack_channel: Slack channel for notifications
        
    Returns:
        n8n workflow JSON dict
    """
    return {
        "name": f"Alert to Jira Ticket",
        "description": f"Creates Jira tickets from {alert_webhook} alerts",
        "nodes": [
            {
                "parameters": {
                    "path": alert_webhook,
                    "responseMode": "onReceived",
                },
                "name": "Alert Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300],
            },
            {
                "parameters": {
                    "authentication": "apiKey",
                    "project": jira_project,
                    "summary": "{{ $json.alert_name }}",
                    "description": "{{ $json.description }}",
                    "issuetype": "Bug",
                },
                "name": "Create Jira",
                "type": "n8n-nodes-base.jira",
                "typeVersion": 1,
                "position": [450, 300],
            },
            {
                "parameters": {
                    "authentication": "oAuth2",
                    "channel": slack_channel,
                    "messageType": "text",
                    "text": "Alert: {{ $json.alert_name }} → Jira {{ $json.id }}",
                },
                "name": "Notify Slack",
                "type": "n8n-nodes-base.slack",
                "typeVersion": 2,
                "position": [650, 300],
            },
        ],
        "connections": {
            "Alert Webhook": {
                "main": [
                    [{"node": "Create Jira", "type": "main", "index": 0}]
                ]
            },
            "Create Jira": {
                "main": [
                    [{"node": "Notify Slack", "type": "main", "index": 0}]
                ]
            },
        },
        "active": False,
        "settings": {
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
        },
        "tags": ["alerting", "jira", "devops"],
    }
