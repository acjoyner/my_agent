# ══════════════════════════════════════════════════════════════════════════════
# Agent configuration
# Edit these values to match your preferences before running.
# ══════════════════════════════════════════════════════════════════════════════

# ── Your profile ──────────────────────────────────────────────────────────────
MY_NAME        = "Anthony Joyner"
MY_LOCATION    = "Charlotte, NC"          # or "remote"

# ── Job search defaults ───────────────────────────────────────────────────────
JOB_TITLE_INTERESTS = [
    "Generative AI Engineer",
    "AI/ML Engineer",
    "LLM Engineer",
    "Software Engineer",
    "Data Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Solutions Architect",
]
MIN_SALARY     = 70_000                   # USD
PREFER_REMOTE  = True

# ── Business interest areas ───────────────────────────────────────────────────
BUSINESS_INTEREST_AREAS = [
    "AI tools",
    "e-commerce",
    "health and wellness",
    "B2B SaaS",
]

# ── Notifications ─────────────────────────────────────────────────────────────
# Set to True to enable desktop notifications
DESKTOP_NOTIFICATIONS = True

# Email via Gmail (requires Google OAuth — run: python tools/google_tools.py --auth)
EMAIL_NOTIFICATIONS = True

# Telegram (requires TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in .env)
TELEGRAM_NOTIFICATIONS = True

# ── Ollama fallback ───────────────────────────────────────────────────────────
# Used automatically when Anthropic API usage limit is hit.
# Requires Ollama running locally: https://ollama.com
OLLAMA_FALLBACK        = True
OLLAMA_BASE_URL        = "http://localhost:11434/v1"
OLLAMA_MODEL           = "gemma4"            # must support tool calling
OLLAMA_FALLBACK_MODELS = [                   # tried in order if primary fails
    "gemma4",
    "llama3.2:latest",
    "qwen3-coder:30b",
]

# ── Google Workspace ──────────────────────────────────────────────────────────
# Path to your OAuth credentials file downloaded from Google Cloud Console.
# After downloading, save it as credentials.json in the project root.
GOOGLE_CREDENTIALS_FILE = "credentials.json"   # relative to project root
GOOGLE_TOKEN_FILE       = "token.json"          # auto-created after first auth

# ── Scheduled scans (used by scheduler.py) ───────────────────────────────────
# How often to auto-run scans (in hours)
JOB_SCAN_INTERVAL_HOURS   = 24
TREND_SCAN_INTERVAL_HOURS = 48

# ── Resume ─────────────────────────────────────────────────────────────────────
RESUME_TEXT = """
Full-Stack Software Engineer & IT Application Analyst with 10+ years of experience in
Enterprise Scalability, Cybersecurity Compliance (NERC CIP), and Cloud-Native Development.
Proven track record in Workflow Automation and System Architecture across Finance and Energy sectors.

TECHNICAL SKILLS
- Languages: Java, Python (Expert), JavaScript/TypeScript (Proficient), HTML5, CSS3
- Frameworks: React, Angular, Django, Flask, Express.js
- API & Integration: RESTful APIs, Confluent Kafka (Event Streaming)
- AI & Automation: Model Training (ML), Workflow Automation, LLM Integration
- Cloud: AWS (EC2, S3, IAM), Supabase (BaaS)
- Containers/DevOps: Docker, CI/CD Pipelines, Git/GitHub, Nginx
- Databases: PostgreSQL, MySQL, SQLite, NoSQL, Informatica, Data Virtualization
- Security/Compliance: NERC CIP Standards (002-014), Cyber Asset Lifecycle (Archer), Tripwire IP360, Panorama

WORK EXPERIENCE
- IT Application Analyst, Duke Energy (June 2018 – March 2026): NERC CIP compliance, Archer asset lifecycle,
  firewall security (CIP-005), audit readiness, infrastructure provisioning.
- IT Instructor, NC A&T (Jan 2018 – 2024): Taught Python, Linux, Java, Web Systems.
- IT Associate III, Duke Energy (Nov 2019 – June 2020): Workload automation (79% manual reduction), Informatica/ETL.
- IT Associate III (ADMS), Duke Energy (June 2018 – Nov 2019): SCADA, automation scripts, CI/CD pipelines.
- IT Associate II, Duke Energy (June 2017 – July 2018): Application development and support.
- VP Senior Auditor I, Bank of America (June 2013 – May 2017): Enterprise audits, controls testing, QA (81% score improvement).

EDUCATION
- M.S. Information Technology, NC A&T State University, May 2017
- B.S. Computer Technology, NC A&T State University, May 2012

KEY PROJECTS
- Full-Stack Cloud Inventory & Asset Manager: React frontend, Supabase/PostgreSQL, Docker, Nginx, RLS security.
- Critical Infrastructure Data Hub (CIDH): Python Kafka clients, Tripwire vulnerability automation, Confluent migration.
- Boundary Electronic Access Review (BEAR): Angular, Panorama firewall automation, compliance dashboards.
""".strip()
