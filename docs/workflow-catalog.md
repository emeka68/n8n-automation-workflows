# Workflow Catalog

Complete reference for all included workflows.

---

## 1. Lead Routing to Slack

**File:** `workflows/lead-routing-slack.json`

**Purpose:** Enriches incoming sales leads with company data and routes them to Slack channels based on lead quality score.

**Trigger Type:** Webhook

**Integrations Used:**
- Clearbit (enrichment)
- Slack (notifications)

**Workflow Steps:**
1. Receive lead data via webhook (`/leads`)
2. Parse incoming JSON payload
3. Enrich with Clearbit company data
4. Score lead quality based on criteria
5. Route to `#hot-leads` (score > 75) or `#warm-leads` (otherwise)

**Webhook Payload Example:**
```json
{
  "email": "contact@company.com",
  "company": "Company Name",
  "score": 85
}
```

**Slack Output:**
- **Hot Leads:** 🔥 Hot Lead Incoming with company name, email, score
- **Warm Leads:** 📊 Warm Lead with same details

**Import Instructions:**
1. Copy `workflows/lead-routing-slack.json` content
2. In n8n, click "Import" → paste JSON
3. Configure Clearbit credentials
4. Configure Slack OAuth2 (requires read:channels, chat:write)
5. Update channel names if needed
6. Activate workflow

**Configuration Variables:**
- `CLEARBIT_API_KEY` — Your Clearbit API key
- Slack channels — Customize #hot-leads and #warm-leads

---

## 2. CRM Sync HubSpot

**File:** `workflows/crm-sync-hubspot.json`

**Purpose:** Syncs contact data between external sources and HubSpot, with automated email confirmation.

**Trigger Type:** Webhook

**Integrations Used:**
- HubSpot CRM (contact creation)
- Gmail (confirmation emails)

**Workflow Steps:**
1. Receive contact via webhook (`/webhook/contacts`)
2. Create HubSpot company record with contact details
3. Send welcome email via Gmail
4. Log sync completion

**Webhook Payload Example:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "company": "Acme Corp",
  "phone": "+1-555-0100"
}
```

**Email Template:**
Customizable HTML email welcoming contact to system.

**Import Instructions:**
1. Import JSON into n8n
2. Configure HubSpot API key (Private App)
3. Configure Gmail OAuth2 credentials
4. Test with sample webhook
5. Activate workflow

**Configuration Variables:**
- `N8N_API_KEY` — HubSpot API key
- Email subject and body — Customize welcome message

---

## 3. Alert to Ticket

**File:** `workflows/alert-to-ticket.json`

**Purpose:** Converts monitoring/alerting system webhooks into Jira tickets with Slack notification and audit logging.

**Trigger Type:** Webhook

**Integrations Used:**
- Jira (ticket creation)
- Slack (notifications)
- Google Sheets (audit log)

**Workflow Steps:**
1. Receive alert via webhook (`/webhook/alert`)
2. Check severity level (P1/P2/P3)
3. Create Jira ticket for critical/high severity
4. Post notification to `#incidents` Slack channel
5. Log alert details to Google Sheets audit log

**Webhook Payload Example:**
```json
{
  "alert_name": "High CPU Usage",
  "service": "api-server-01",
  "severity": "critical",
  "description": "CPU usage exceeded 90%",
  "timestamp": "2024-03-20T15:30:00Z"
}
```

**Jira Ticket:**
- Summary: `[CRITICAL] High CPU Usage`
- Type: Bug
- Priority: Highest
- Description: Alert details with timestamp

**Slack Message:**
- Posts to `#incidents`
- Format: 🚨 P1 Incident with alert name, service, Jira link

**Import Instructions:**
1. Import JSON into n8n
2. Configure Jira API key (from account settings)
3. Specify Jira project key (e.g., "OPS")
4. Configure Slack OAuth2
5. Configure Google Sheets access
6. Activate workflow

**Configuration Variables:**
- `N8N_API_KEY` — Jira API key
- Jira project — Change "OPS" to your project
- Slack channel — Update #incidents if needed
- Google Sheet ID — Specify sheet for audit logs

---

## 4. Email to Task

**File:** `workflows/email-to-task.json`

**Purpose:** Monitors Gmail inbox, extracts action items using AI, and creates structured tasks in Notion.

**Trigger Type:** Gmail Label

**Integrations Used:**
- Gmail (email monitoring)
- OpenAI (action item extraction)
- Notion (task database)

**Workflow Steps:**
1. Monitor Gmail for new emails with "Action Items" label
2. Extract email body content
3. Use OpenAI to identify and structure action items
4. Parse AI response as JSON
5. Create Notion database entries with task details

**Gmail Setup:**
- Create a Gmail label called "Action Items"
- Apply to emails containing action items
- Workflow automatically processes tagged emails

**OpenAI Prompt:**
Extracts `task`, `owner`, `due_date` fields from email content.

**Notion Output:**
Creates database entry with:
- Task name
- Owner
- Due date
- Source email address

**Import Instructions:**
1. Import JSON into n8n
2. Configure Gmail OAuth2 credentials
3. Create/specify "Action Items" label
4. Configure OpenAI API key
5. Get Notion database ID (from share link)
6. Configure Notion API integration
7. Activate workflow

**Configuration Variables:**
- `OPENAI_API_KEY` — OpenAI API key
- `NOTION_DATABASE_ID` — Notion database ID
- Gmail label name — Update if using different label name

---

## 5. Daily Report Digest

**File:** `workflows/daily-report-digest.json`

**Purpose:** Scheduled daily aggregation of business metrics with AI-generated summary sent via email and Slack.

**Trigger Type:** Scheduled (Daily at 9:00 AM)

**Integrations Used:**
- Custom API (data source)
- OpenAI (report generation)
- Gmail (email distribution)
- Slack (feed post)

**Workflow Steps:**
1. Trigger at 9:00 AM daily (EST)
2. Fetch sales metrics from custom API
3. Fetch customer metrics from custom API
4. Combine data sources
5. Use OpenAI to generate executive summary
6. Email summary to stakeholders
7. Post summary to `#reports` Slack channel

**Data Sources:**
- Sales metrics endpoint: `{DATA_SOURCE_API_URL}/sales-metrics`
- Customer metrics endpoint: `{DATA_SOURCE_API_URL}/customer-metrics`

**API Requirements:**
Both endpoints should return JSON with relevant metrics.

**Report Content:**
AI-generated executive summary including:
- Key metrics
- Highlights and trends
- Insights and recommendations

**Email Recipients:**
Configure in `REPORT_EMAIL` environment variable (comma-separated for multiple).

**Import Instructions:**
1. Import JSON into n8n
2. Configure data source API URL and key
3. Configure OpenAI API key
4. Configure Gmail OAuth2
5. Configure Slack OAuth2
6. Set schedule (customize trigger time if needed)
7. Activate workflow

**Configuration Variables:**
- `DATA_SOURCE_API_URL` — Your metrics API endpoint
- `DATA_API_KEY` — API authentication key
- `OPENAI_API_KEY` — OpenAI API key
- `REPORT_EMAIL` — Email address(es) for report distribution
- Cron schedule — Modify trigger time if needed

---

## 6. New Customer Onboarding

**File:** `workflows/new-customer-onboarding.json`

**Purpose:** Orchestrates comprehensive customer onboarding including email sequences, CRM creation, team notifications, and newsletter signup.

**Trigger Type:** Webhook

**Integrations Used:**
- HubSpot (company creation)
- Gmail (welcome email)
- Slack (team notification)
- Newsletter API (subscriber management)
- Google Sheets (onboarding log)

**Workflow Steps:**
1. Receive new customer data via webhook (`/webhook/new-customer`)
2. Send personalized welcome email
3. Create HubSpot company record
4. Notify sales team in `#sales-new-customers` Slack channel
5. Add customer email to newsletter list
6. Log onboarding completion to Google Sheets

**Webhook Payload Example:**
```json
{
  "company": "New Startup Inc",
  "contact_name": "Jane Smith",
  "email": "jane@newstartup.com",
  "industry": "Technology",
  "website": "https://newstartup.com"
}
```

**Email Sequence:**
- Welcome email sent with onboarding link
- Customizable template with company name

**HubSpot Record:**
Company created with:
- Company name
- Industry
- Contact email and name
- Website

**Slack Notification:**
Posts to `#sales-new-customers` with:
- Company name
- Contact person
- Email
- Industry classification

**Newsletter Integration:**
Customer email added with source tag "customer_onboarding"

**Import Instructions:**
1. Import JSON into n8n
2. Configure HubSpot API key
3. Configure Gmail OAuth2
4. Configure Slack OAuth2
5. Configure Newsletter API endpoint and key
6. Configure Google Sheets access
7. Update welcome email template
8. Activate workflow

**Configuration Variables:**
- `N8N_API_KEY` — HubSpot API key
- `COMPANY_NAME` — Your company name (in email)
- `ONBOARDING_LINK` — Link to onboarding page
- `NEWSLETTER_API_URL` — Newsletter service endpoint
- `REPORT_EMAIL` — Admin email for logs
- Slack channel — Update #sales-new-customers if needed
- Google Sheet ID — Onboarding log sheet

---

## Workflow Comparison Matrix

| Feature | Lead Routing | CRM Sync | Alert→Ticket | Email→Task | Daily Report | Onboarding |
|---------|-------------|----------|-------------|-----------|--------------|-----------|
| Trigger | Webhook | Webhook | Webhook | Gmail | Scheduled | Webhook |
| Manual Setup | ⚠️ High | Low | Low | ⚠️ Medium | ⚠️ High | ⚠️ High |
| External APIs | 2 | 2 | 3 | 3 | 3 | 5 |
| Customization | Medium | Low | Medium | High | High | High |
| Typical Use | Sales | Sales | DevOps | Productivity | Reporting | Customer Succ |

---

## Best Practices

1. **Start Simple** — Deploy Lead Routing first (fewest dependencies)
2. **Environment Variables** — Never hardcode API keys; use `.env`
3. **Test Webhooks** — Use n8n's webhook test feature before activation
4. **Monitor Execution** — Check execution logs for errors
5. **Backup Workflows** — Use `workflow_manager.py backup` regularly
6. **Document Changes** — Note any customizations for future reference

---

## Troubleshooting

**Workflow not triggering:**
- Check webhook URL is correct
- Verify credentials are valid
- Check execution logs for errors

**Missing data in output:**
- Verify input payload matches expected schema
- Check API responses are returning expected fields
- Add debug nodes to inspect data flow

**Integration errors:**
- Verify API keys are current (often expire)
- Check integrations have necessary permissions
- Review n8n credential configuration

---

## More Information

- [n8n Documentation](https://docs.n8n.io)
- [Workflow Troubleshooting](https://docs.n8n.io/workflows/troubleshooting/)
- [API Reference](https://docs.n8n.io/api/)
