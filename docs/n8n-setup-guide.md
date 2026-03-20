# n8n Setup & Installation Guide

Complete guide to installing n8n, importing workflows, and configuring credentials.

---

## Installation

### Option 1: Docker (Recommended)

**Prerequisites:** Docker and Docker Compose installed

**Quick Start:**
```bash
# Create directory
mkdir n8n
cd n8n

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

volumes:
  n8n_data:
EOF

# Start n8n
docker-compose up -d

# Access at http://localhost:5678
```

**With PostgreSQL Backend (Production):**
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: n8n_password
      POSTGRES_DB: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n_password
      - DB_POSTGRESDB_DATABASE=n8n
      - NODE_ENV=production
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  n8n_data:
  postgres_data:
EOF

docker-compose up -d
```

### Option 2: npm (Local Development)

```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n

# Access at http://localhost:5678
```

### Option 3: Self-Hosted (Advanced)

See [n8n Self-Hosted Documentation](https://docs.n8n.io/hosting/installation/docker/)

---

## Initial Setup

1. **Access n8n:** Open http://localhost:5678
2. **Create Account:** Set up your admin user
3. **First Login:** Access the main dashboard

---

## Importing Workflows

### Method 1: JSON Upload (Easiest)

1. In n8n, click **"Workflows"** → **"New"** (or import button)
2. Click **"Import"** → **"From JSON"**
3. Copy and paste content from workflow JSON file
4. Click **"Import"**
5. Workflow appears in your list (inactive)

### Method 2: Using Python CLI

```bash
# List available workflows
python workflow_manager.py list

# Validate before importing
python workflow_manager.py validate workflows/lead-routing-slack.json

# Deploy directly (requires API key)
python workflow_manager.py deploy workflows/lead-routing-slack.json
```

### Method 3: Manual Creation

Copy nodes manually from workflow JSON if UI import fails.

---

## Configuring Credentials

### Slack Integration

1. Go to n8n **Credentials** → **New**
2. Select **Slack**
3. Authenticate with your Slack workspace
4. Grant permissions:
   - `chat:write` — Send messages
   - `channels:read` — List channels
   - `users:read` — List users
5. **Save** and use in workflows

### Gmail Integration

1. **Credentials** → **New** → **Gmail**
2. Click **"Authenticate"**
3. Sign in with Google account
4. Grant permissions for email access
5. **Save**

### HubSpot Integration

1. Create HubSpot **Private App**
   - Log in to HubSpot
   - Settings → Integrations → Private Apps
   - Create new app with scopes:
     - `crm.objects.contacts.read`
     - `crm.objects.contacts.write`
     - `crm.objects.companies.read`
     - `crm.objects.companies.write`

2. In n8n:
   - **Credentials** → **New** → **HubSpot**
   - Paste access token from HubSpot
   - **Save**

### OpenAI Integration

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. In n8n:
   - **Credentials** → **New** → **OpenAI**
   - Paste API key
   - **Save**

### Jira Integration

1. Generate API token from Jira
   - Jira Cloud: Profile → Security → API tokens
   - Create new token, copy it

2. In n8n:
   - **Credentials** → **New** → **Jira**
   - Email: Your Jira email
   - API Token: Generated token
   - **Save**

### Google Sheets Integration

1. **Credentials** → **New** → **Google Sheets**
2. Click **"Authenticate"**
3. Sign in and grant spreadsheet access
4. **Save**

### Custom API Integration

1. **Credentials** → **New** → **API Key (Generic)**
2. Enter API key name and value
3. **Save**
4. Use in HTTP Request nodes

---

## Environment Variables

Create `.env` file in project root:

```env
# n8n Instance Configuration
N8N_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key_here

# Integration Keys
CLEARBIT_API_KEY=your_clearbit_key
OPENAI_API_KEY=your_openai_key
DATA_API_KEY=your_data_api_key

# API Endpoints
DATA_SOURCE_API_URL=https://api.yourcompany.com
NEWSLETTER_API_URL=https://newsletter.yourcompany.com

# Configuration
COMPANY_NAME=Your Company Name
ONBOARDING_LINK=https://onboard.yourcompany.com
REPORT_EMAIL=reports@yourcompany.com
NOTION_DATABASE_ID=your_notion_db_id
```

Load in Python code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

---

## Webhook Configuration

### Getting Your Webhook URL

1. In n8n, add a **Webhook** node to your workflow
2. Click on the node
3. Copy the URL under "Webhook URL"
4. Example: `https://your-n8n-domain.com/webhook/abc123`

### Testing Webhooks

**Using curl:**
```bash
curl -X POST https://your-n8n-domain.com/webhook/lead-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "company": "Test Corp",
    "score": 80
  }'
```

**Using n8n Test Execution:**
1. In workflow editor, click **"Webhook Node"** → **"Test"**
2. Use provided test link
3. Send request from another terminal

### Exposing Local n8n to External Services

For webhooks from external APIs:

**Using ngrok (Temporary):**
```bash
# Install ngrok
brew install ngrok  # macOS
choco install ngrok # Windows
sudo apt install ngrok-client # Linux

# Start tunnel
ngrok http 5678

# Your public webhook URL:
# https://abc123.ngrok.io/webhook/my-webhook
```

**Using SSH Tunnel (SSH Server Required):**
```bash
ssh -R 5678:localhost:5678 user@remote-server
```

---

## Python Toolkit Setup

### Installation

```bash
# Clone repository
git clone https://github.com/emeka68/n8n-automation-workflows.git
cd n8n-automation-workflows

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage Examples

**List Workflows:**
```bash
python workflow_manager.py list
```

**Validate Workflow:**
```bash
python workflow_manager.py validate workflows/lead-routing-slack.json
```

**Deploy Workflow:**
```bash
python workflow_manager.py deploy workflows/lead-routing-slack.json
```

**Backup All Workflows:**
```bash
python workflow_manager.py backup --output backup_20240320.json
```

**Using n8n Client:**
```python
from n8n_client import N8nClient

client = N8nClient()

# List workflows
workflows = client.list_workflows()
print(f"Total: {len(workflows)}")

# Get specific workflow
wf = client.get_workflow("workflow-id-here")
print(wf['name'])

# Activate workflow
client.activate_workflow("workflow-id-here")

# Deactivate workflow
client.deactivate_workflow("workflow-id-here")
```

**Generating Workflows Programmatically:**
```python
from workflow_templates import create_webhook_to_slack
from n8n_client import N8nClient

# Generate workflow
wf_json = create_webhook_to_slack(
    webhook_path="/webhook/alerts",
    slack_channel="#alerts",
    message_template="New Alert: {{ $json.message }}"
)

# Deploy
client = N8nClient()
result = client.create_workflow(wf_json)
print(f"Created workflow: {result['id']}")
```

---

## Executing Workflows

### Manual Execution

1. Open workflow in n8n
2. Click **"Execute Workflow"** button
3. Monitor execution logs

### Webhook-Triggered Execution

Send data to webhook URL:
```bash
curl -X POST https://your-instance/webhook/path \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### Scheduled Execution

Workflows with **Schedule Trigger** run automatically at configured times.

### Programmatic Execution

```python
# Query execution history
client = N8nClient()
executions = client.get_workflow_executions("workflow-id", limit=10)

for exec in executions:
    print(f"Status: {exec['status']}, Duration: {exec['duration']}ms")
```

---

## Monitoring & Debugging

### Execution Logs

1. Open workflow
2. Click **"Executions"** tab
3. View detailed logs for each execution
4. Check error messages for troubleshooting

### Debug Mode

Add **Debug** node in workflows to inspect data at each step:

```json
{
  "type": "n8n-nodes-base.debugOutput",
  "name": "Debug",
  "parameters": {
    "description": "Check data here"
  }
}
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Webhook not triggering | Check URL is correct, test with curl |
| API key errors | Verify credentials are fresh (some keys expire) |
| Missing data | Check input payload matches expected format |
| Timeout errors | Increase node timeout in advanced settings |
| Memory errors | Reduce workflow complexity or add batch processing |

---

## Production Deployment

### Security Checklist

- [ ] Use HTTPS (not HTTP)
- [ ] Set strong passwords
- [ ] Rotate API keys regularly
- [ ] Use environment variables for secrets
- [ ] Enable webhook authentication
- [ ] Monitor execution logs
- [ ] Set up error notifications

### Performance Tips

1. **Batch Processing** — Process large datasets in chunks
2. **Rate Limiting** — Respect external API rate limits
3. **Caching** — Store frequently accessed data
4. **Error Handling** — Use Try/Catch nodes

### Scaling

- Use PostgreSQL backend for multiple users
- Configure read replicas for high traffic
- Use message queues for async processing
- Monitor resource usage (CPU, memory, disk)

---

## Updates & Maintenance

### Updating n8n

```bash
# Docker
docker-compose pull
docker-compose up -d

# npm
npm update -g n8n
```

### Backing Up

```bash
# Using Python CLI
python workflow_manager.py backup --output backup.json

# Docker volumes
docker run --rm -v n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n-backup.tar.gz /data
```

### Restoring

```bash
# Upload backup.json through n8n UI import, or
# Restore Docker volume from backup
docker run --rm -v n8n_data:/data -v $(pwd):/backup alpine tar xzf /backup/n8n-backup.tar.gz -C /
```

---

## Additional Resources

- **Official Docs:** https://docs.n8n.io
- **Community Forum:** https://community.n8n.io
- **Node Library:** https://n8n.io/nodes
- **GitHub:** https://github.com/n8n-io/n8n

---

## Support

For issues with this workflow library:
- Check `docs/workflow-catalog.md`
- Review workflow JSON comments
- Test with simple webhook first
- Check n8n execution logs

For n8n-specific issues:
- Consult official documentation
- Search community forum
- File GitHub issue on n8n repo
