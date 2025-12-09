# GitHub Secrets Required for AiFinOps Enterprise

These secrets MUST be created in:
GitHub → Repo → Settings → Secrets and variables → Actions

---

## 🔐 1. AWS Credentials for CI Jobs
### CI_AWS_ACCESS_KEY_ID  
Used by GitHub Actions to ingest AWS billing data.

### CI_AWS_SECRET_ACCESS_KEY  
Secret key paired with the access key.

**Permissions needed**:  
- ce:GetCostAndUsage  
- ec2:DescribeInstances  
- s3:ListBuckets

---

## 🔐 2. OPENAI_API_KEY  
Needed if LLM_PROVIDER=openai.  
Used by explain-bill, anomaly explanations, and PR generation.

---

## 🔐 3. ANTHROPIC_API_KEY  
Used only if Claude fallback is enabled.

---

## 🔐 4. GEMINI_API_KEY  
Used only if Gemini fallback is enabled.

---

## 🔐 5. XAI_API_KEY  
Optional — one day when xAI credits exist.

---

## 🔐 6. GITHUB_TOKEN (Personal Access Token recommended)
Required for:
- Creating PRs from GitHub Actions
- Writing commits from workflows
- Managing new branches created by AiFinOps

**Scopes needed:**  
- repo  
- workflow  

---

## 🔐 7. SLACK_WEBHOOK_URL  
Used for FinOps alerts in Slack:
- Daily bill summary  
- Anomalies detected  
- PR opened  
- Cost spike warnings  

---

## 🔐 8. STREAMLIT_CLOUD_EMAIL (optional)
Used only for automatic deploy triggers.

---

# All secrets must be stored as GitHub ACTIONS secrets — NEVER in .env committed to the repo.
