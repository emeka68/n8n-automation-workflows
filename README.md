# n8n Automation Workflows

Production-ready n8n workflow library with Python management toolkit for common business automation use cases.

**Portfolio piece for landing n8n automation jobs on Upwork.**

---

## What's Included

### 6 Production-Ready Workflow Templates

| Workflow | Trigger | Key Integrations | Use Case |
|----------|---------|------------------|----------|
| **Lead Routing to Slack** | Webhook | Clearbit, Slack | Sales automation - enriches and scores incoming leads |
| **CRM Sync HubSpot** | Webhook | HubSpot, Gmail | Contact management - syncs data and sends confirmations |
| **Alert to Ticket** | Webhook | Jira, Slack, Google Sheets | DevOps - routes alerts to Jira tickets |
| **Email to Task** | Gmail | OpenAI, Notion | Productivity - extracts action items from emails |
| **Daily Report Digest** | Scheduled (9am) | Custom API, Gmail, Slack | Reporting - aggregates metrics and sends summaries |
| **New Customer Onboarding** | Webhook | HubSpot, Gmail, Slack | Customer success - orchestrates multi-step onboarding |

### Python Toolkit

- **`workflow_manager.py`** — CLI for workflow operations
  - `list` — See all workflows with metadata
  - `validate` — Check JSON schema validity
  - `deploy` — Upload workflow to n8n instance
  - `backup` — Export all workflows from n8n
  
- **`n8n_client.py`** — REST API wrapper
  - List, create, update, activate/deactivate, delete workflows
  - Query execution history
  
- **`workflow_templates.py`** — Programmatic generators
  - Generate common workflow patterns in code
  - Reusable functions for webhook→Slack, scheduled reports, alerts→tickets

---

## Quick Start

### Prerequisites

- Python 3.8+
- n8n instance running (Docker or self-hosted)
- API credentials for integrations (Slack, HubSpot, etc.)

### Installation

```bash
git clone https://github.com/emeka68/n8n-automation-workflows.git
cd n8n-automation-workflows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your n8n URL and API key
```

### Deploy a Workflow

```bash
# List available workflows
python workflow_manager.py list

# Validate before deploying
python workflow_manager.py validate workflows/lead-routing-slack.json

# Deploy to n8n
python workflow_manager.py deploy workflows/lead-routing-slack.json
```

### Using the Python API

```python
from n8n_client import N8nClient
from workflow_templates import create_webhook_to_slack

# Create client
client = N8nClient()

# List workflows
workflows = client.list_workflows()
print(f"Found {len(workflows)} workflows")

# Generate and deploy a new workflow
wf_json = create_webhook_to_slack(
    webhook_path="/webhook/custom-alerts",
    slack_channel="#ops",
    message_template="Alert: {{ $json.message }}"
)
result = client.create_workflow(wf_json)
print(f"Deployed workflow {result['id']}")
```

---

## Workflow Details

### Lead Routing to Slack
Incoming leads are enriched with company data via Clearbit, scored for quality, and routed to different Slack channels based on score.

**Setup:**
1. Create webhook trigger in n8n pointing to this workflow
2. Configure Clearbit credentials in n8n
3. Configure Slack OAuth2 integration
4. Map Slack channels for #hot-leads and #warm-leads

**Example Webhook Payload:**
```json
{
  "email": "buyer@techcompany.com",
  "company": "TechCorp Inc",
  "score": 85
}
```

### CRM Sync HubSpot
Syncs new contacts between systems, creates HubSpot company records, and sends confirmation emails.

**Integrations:** HubSpot, Gmail

**Flow:**
- Webhook trigger receives contact data
- Creates HubSpot company record
- Sends welcome email via Gmail
- Logs sync completion

### Alert to Ticket
Transforms monitoring alerts into Jira tickets, notifies Slack, and maintains an audit log in Google Sheets.

**Integrations:** Jira, Slack, Google Sheets

**Flow:**
- Webhook receives alert from monitoring system
- Checks severity level
- Creates Jira ticket (P1/P2 only)
- Posts notification to #incidents channel
- Logs to audit sheet

### Email to Task
Reads Gmail labels, uses OpenAI to extract action items, and creates tasks in Notion.

**Integrations:** Gmail, OpenAI, Notion

**Flow:**
- Gmail trigger on new emails with "Action Items" label
- OpenAI extracts structured task data
- Creates Notion database entries
- Tracks owner and due dates

### Daily Report Digest
Scheduled daily at 9am. Aggregates data from multiple sources, generates AI summary, and distributes via email + Slack.

**Integrations:** Custom API, OpenAI, Gmail, Slack

**Flow:**
- Scheduled trigger (9am daily)
- Fetches sales metrics and customer data
- AI generates executive summary
- Email distribution to stakeholders
- Slack #reports channel post

### New Customer Onboarding
Orchestrates multi-step onboarding: welcome email, CRM record creation, sales team notification, newsletter signup.

**Integrations:** HubSpot, Gmail, Slack, Newsletter API

**Flow:**
- Webhook on new customer signup
- Sends personalized welcome email
- Creates HubSpot company record
- Notifies #sales-new-customers channel
- Auto-adds to newsletter
- Logs to Google Sheets

---

## Architecture

```
n8n-automation-workflows/
├── workflows/                   # n8n JSON exports
│   ├── lead-routing-slack.json
│   ├── crm-sync-hubspot.json
│   ├── alert-to-ticket.json
│   ├── email-to-task.json
│   ├── daily-report-digest.json
│   └── new-customer-onboarding.json
├── n8n_client.py               # REST API client
├── workflow_templates.py        # Programmatic generators
├── workflow_manager.py          # CLI tool
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── docs/
    ├── workflow-catalog.md      # Detailed workflow docs
    └── n8n-setup-guide.md       # Installation guide
```

---

## Environment Configuration

Create `.env` file with:

```env
# n8n Instance
N8N_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here

# External APIs
CLEARBIT_API_KEY=your_clearbit_key
OPENAI_API_KEY=your_openai_key
DATA_SOURCE_API_URL=https://your-api.example.com
DATA_API_KEY=your_data_api_key

# Configuration
COMPANY_NAME=Your Company
ONBOARDING_LINK=https://onboarding.example.com
REPORT_EMAIL=reports@example.com
NOTION_DATABASE_ID=your_notion_db_id
NEWSLETTER_API_URL=https://newsletter-api.example.com
```

---

## Use Cases

### Sales Automation
- **Lead Routing** — Auto-segment and score inbound leads
- **Contact Sync** — Keep CRM data in sync across systems
- **Onboarding** — Automated customer success workflows

### DevOps & Incident Management
- **Alert Automation** — Convert alerts to tracked tickets
- **Incident Response** — Notify teams and log issues
- **Status Reporting** — Aggregate metrics and send daily summaries

### Productivity & Task Management
- **Email Processing** — Extract action items from emails
- **Task Creation** — Auto-populate task management tools
- **Reporting** — Scheduled data aggregation and distribution

---

## CLI Commands

### List Workflows
```bash
python workflow_manager.py list
```
Shows all available workflow files with metadata.

### Validate Workflow
```bash
python workflow_manager.py validate workflows/lead-routing-slack.json
```
Checks JSON schema and required fields.

### Deploy Workflow
```bash
python workflow_manager.py deploy workflows/lead-routing-slack.json \
  --n8n-url http://localhost:5678 \
  --api-key your_api_key
```

### Backup All Workflows
```bash
python workflow_manager.py backup \
  --n8n-url http://localhost:5678 \
  --api-key your_api_key \
  --output backup_2024_03_20.json
```

---

## Customization

All workflows are JSON templates. Customize by:

1. **Editing fields:** Modify Slack channels, email templates, etc.
2. **Changing nodes:** Replace integrations with your own tools
3. **Using Python generators:** Use `workflow_templates.py` to programmatically build custom workflows

Example:
```python
from workflow_templates import create_webhook_to_slack

# Generate custom workflow
wf = create_webhook_to_slack(
    webhook_path="/webhook/my-app",
    slack_channel="#alerts",
    message_template="Custom: {{ $json.data }}"
)

# Deploy it
client.create_workflow(wf)
```

---

## Support

For issues or feature requests, check n8n docs: https://docs.n8n.io

---

## Author

**Nnaemeka Duru**  
Email: emekaduru09@gmail.com  
LinkedIn: [emeka-duru](https://linkedin.com/in/emeka-duru)

---

## License

MIT License - use freely for portfolio and commercial projects.

---

Made with ❤️ for n8n automation professionals.
