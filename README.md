# Personal Assistant Agent

A fully autonomous AI agent powered by Claude that researches jobs, scans business
trends, and acts as your personal assistant — all from the terminal.

---

## What it does

| Capability | Examples |
|---|---|
| **Job research** | Search remote jobs by title, salary, location across multiple boards |
| **Trend analysis** | Spot rising industries, underserved niches, growth signals |
| **Business ideas** | Find problems people pay to solve with evidence from the web |
| **File saving** | Auto-saves research results to Markdown files in `output/` |
| **Notifications** | Desktop alert + log when it finds something important |
| **Memory** | Remembers your preferences across sessions |
| **Scheduling** | Auto-runs daily job scans and weekly trend reports |

---

## Project structure

```
my_agent/
├── agent.py            ← Main entry point (run this)
├── scheduler.py        ← Automated daily/weekly scans
├── requirements.txt
├── config/
│   └── settings.py     ← YOUR preferences (edit this first)
├── tools/
│   ├── web_search.py   ← General web search
│   ├── job_search.py   ← Job board search
│   ├── trends.py       ← Trend + business idea research
│   ├── file_tools.py   ← Save/read files
│   └── notify.py       ← Desktop + log notifications
├── memory/
│   └── memory.py       ← Persistent memory across sessions
└── output/             ← All saved files go here
```

---

## Setup (5 minutes)

### 1. Install Python
Download from https://python.org — version 3.10 or higher.

### 2. Get your Anthropic API key
Go to https://console.anthropic.com, sign up, and create an API key.

### 3. Set your API key

**Mac / Linux** — add to your `~/.zshrc` or `~/.bashrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
Then: `source ~/.zshrc`

**Windows** — in Command Prompt:
```cmd
setx ANTHROPIC_API_KEY "sk-ant-..."
```
Restart your terminal after this.

### 4. Install dependencies
```bash
cd my_agent
pip install -r requirements.txt
```

### 5. Edit your preferences
Open `config/settings.py` and fill in:
- Your name and location
- Job titles you're interested in
- Minimum salary
- Whether you prefer remote
- Business areas you're watching

### 6. Run it
```bash
python agent.py
```

---

## Usage examples

Type these at the `You:` prompt:

```
Find remote marketing jobs paying over 80k

What are the hottest AI tool trends right now?

Research business ideas in the health and wellness space with low startup costs

Search for product manager jobs in Charlotte NC

What business opportunities exist in e-commerce right now?

Save a weekly summary of tech industry trends

What jobs have you found so far? List the saved files.

I prefer remote work and am targeting at least $90,000 salary
```

The agent will remember anything you tell it about your preferences.

---

## Automated scans (optional)

Run scans automatically without opening the terminal:

**Run once right now:**
```bash
python scheduler.py
```

**Keep running on a schedule (leave terminal open):**
```bash
python scheduler.py --loop
```

**Run automatically every morning at 8am (Mac/Linux):**
```bash
crontab -e
```
Add this line (update the path):
```
0 8 * * * cd /Users/yourname/my_agent && python scheduler.py >> output/scheduler.log 2>&1
```

---

## How it works (the agent loop)

```
You give a goal
      ↓
Claude reasons: "what tools do I need?"
      ↓
Claude calls a tool (web search, job search, etc.)
      ↓
Tool runs, result returned to Claude
      ↓
Claude decides: done? or call another tool?
      ↓
Loops until complete, then responds to you
```

This is the **ReAct loop**: Reason → Act → Observe → Repeat.

---

## Adding your own tools

A tool is just a Python function. To add one:

1. Create a function in `tools/my_tool.py`
2. Add it to the `TOOLS` list in `agent.py` with a description
3. Add it to the `dispatch` dict in `run_tool()` in `agent.py`

Claude will automatically decide when to use it based on your description.

---

## Connecting external services with MCP

MCP (Model Context Protocol) lets Claude connect to services like Gmail, Google
Calendar, Notion, GitHub, Slack, and more — without writing custom integration code.

To add an MCP server:
1. Install Claude Code: `npm install -g @anthropic-ai/claude-code`
2. Run: `claude mcp add`
3. Choose from the registry (Gmail, Google Drive, Notion, etc.)
4. The tool becomes available in your agent automatically

Full MCP docs: https://docs.claude.ai/mcp

---

## Cost estimate

Each agent run makes 1-5 API calls depending on complexity.
- Simple question: ~$0.001
- Job search + save: ~$0.01
- Full trend report: ~$0.02-0.05
- Daily automated scan: ~$0.05-0.10/day

At typical usage this is $1-5/month.

---

## Troubleshooting

**"ANTHROPIC_API_KEY not set"** → Make sure you set the environment variable and
restarted your terminal.

**"Module not found"** → Run `pip install -r requirements.txt` from inside the
`my_agent` folder.

**Slow responses** → Normal for complex tasks. The agent is making multiple API
calls and web searches. Typical response: 10-30 seconds.

**No desktop notifications** → Notifications are logged to `output/notifications.log`
regardless. Desktop alerts require `osascript` (Mac), `notify-send` (Linux), or
PowerShell (Windows).
# my_agent
