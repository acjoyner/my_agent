cat tools/skills.py
cat tools/skills.py
cat app.py
cat << 'EOF' > migrate.py
import os
import re

def migrate_agent_py():
    with open('agent.py', 'r') as f:
        content = f.read()
    
    
    # Update stream_agent_ollama to use gemma4 model
    # Look for ollama.chat call or similar
    content = re.sub(r'(model\s*=\s*)[^,)]+', r'\1"gemma4"', content)
    
    # Replace stream_agent logic
    stream_agent_pattern = r'(def stream_agent\(user_message: str, memory: Memory\) -> str:).*?(?=\ndef|$)'
    new_body = r'\1\n    return stream_agent_ollama(user_message, memory, model="gemma4")'
    content = re.sub(stream_agent_pattern, new_body, content, flags=re.DOTALL)
    
    with open('agent.py', 'w') as f:
        f.write(content)

def migrate_tools():
    tools = ['skills.py', 'teach.py', 'job_search.py', 'trends.py', 'web_search.py']
    for tool in tools:
        path = os.path.join('tools', tool)
        if os.path.exists(path):
            with open(path, 'r') as f:
                lines = f.readlines()
            with open(path, 'w') as f:
                for line in lines:
                        continue
                    f.write(line)

def migrate_requirements():
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    with open('requirements.txt', 'w') as f:
        for line in lines:
            if 'anthropic' in line:
                f.write('ollama\n')
            else:
                f.write(line)

def migrate_app_py():
    with open('app.py', 'r') as f:
        content = f.read()
    # Ensure agent calls point to ollama implementation
    # This assumes we want to change any call that looks like an agent call
    # But since we updated stream_agent in agent.py to call ollama, maybe no change needed in app.py
    # Let's just double check if there are specific anthropic mentions
    with open('app.py', 'w') as f:
        f.write(content)

migrate_agent_py()
migrate_tools()
migrate_requirements()
migrate_app_py()
EOF
python3 migrate.py
cat requirements.txt
cat requirements.txt
cat requirements.txt; grep "stream_agent" agent.py; ls tools/
cat requirements.txt; grep -C 5 "stream_agent" agent.py; grep "anthropic" tools/skills.py
"""
Personal Assistant Agent
Researches jobs, business trends, and handles personal assistant tasks.
Run: python agent.py
"""

from dotenv import load_dotenv
load_dotenv()


import json
from tools.web_search   import search_web
from tools.job_search   import search_jobs, get_job_details
from tools.trends       import search_trends, search_business_ideas
from tools.skills       import analyze_skill_gap, find_learning_resources, get_in_demand_skills
from tools.teach        import generate_lesson, quiz_me, update_progress, get_study_plan, parse_job_description
from tools.file_tools   import save_to_file, read_file, list_saved_files
from tools.notify       import send_notification, send_email, send_telegram
from tools.google_tools import (
    sheets_create, sheets_read, sheets_write, sheets_append,
    docs_create, docs_read,
    slides_create, slides_read, slides_add_slide,
    gmail_read_inbox, gmail_get_message, gmail_search, gmail_mark_read,
    drive_list, drive_upload,
)
from memory.memory      import Memory
from config.settings    import RESUME_TEXT

# ── Tool registry ──────────────────────────────────────────────────────────────
# Each entry describes a tool to Claude. Claude decides when to call them.

TOOLS = [
    {
        "name": "search_web",
        "description": (
            "Search the web for any topic. Use for general research, news, "
            "current events, or anything not covered by the specialised tools."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results (default 5)", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_jobs",
        "description": (
            "Search for job listings. Searches multiple job boards. "
            "Filter by title, location, salary, remote, and keywords."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title":    {"type": "string",  "description": "Job title or role (e.g. 'Marketing Manager')"},
                "location": {"type": "string",  "description": "City, state, or 'remote'"},
                "min_salary":{"type": "integer","description": "Minimum salary in USD"},
                "keywords": {"type": "array",   "items": {"type": "string"}, "description": "Extra keywords to filter by"},
                "remote":   {"type": "boolean", "description": "Only show remote jobs"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_job_details",
        "description": "Get full details for a specific job listing by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Job ID from search_jobs results"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "search_trends",
        "description": (
            "Search for current trends in any industry or topic. "
            "Returns trending topics, growth signals, and news."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic":    {"type": "string", "description": "Industry or topic (e.g. 'AI tools', 'e-commerce')"},
                "timeframe":{"type": "string", "description": "'week', 'month', or 'year' (default: month)", "default": "month"}
            },
            "required": ["topic"]
        }
    },
    {
        "name": "search_business_ideas",
        "description": (
            "Find underserved niches and business opportunities in a given area. "
            "Returns pain points, gaps in the market, and emerging opportunities."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "area":    {"type": "string", "description": "Business area or interest (e.g. 'fitness', 'B2B SaaS')"},
                "budget":  {"type": "string", "description": "Budget range: 'low', 'medium', 'high'", "default": "low"}
            },
            "required": ["area"]
        }
    },
    {
        "name": "save_to_file",
        "description": (
            "Save research results, job lists, notes, or learning docs to a file. "
            "Use the folder parameter to organise by type: "
            "'jobs' for job results, 'trends' for market research, "
            "'learning' for study notes and project docs, 'skills' for skill reports."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Filename without extension (e.g. 'remote_jobs_march')"},
                "content":  {"type": "string", "description": "Content to save"},
                "format":   {"type": "string", "description": "'txt', 'md', or 'json'", "default": "md"},
                "folder":   {"type": "string", "description": "Subfolder: 'jobs', 'trends', 'learning', 'skills', or leave empty for root"}
            },
            "required": ["filename", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a previously saved file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Filename to read"}
            },
            "required": ["filename"]
        }
    },
    {
        "name": "list_saved_files",
        "description": "List all files saved by the agent.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "analyze_skill_gap",
        "description": (
            "Compare the user's current skills against what's required for a target job. "
            "Returns matched skills, missing skills ranked by importance, and a competitive assessment."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title":      {"type": "string", "description": "Target job title (e.g. 'Senior Product Manager')"},
                "current_skills": {"type": "string", "description": "Comma-separated list of the user's current skills"}
            },
            "required": ["job_title", "current_skills"]
        }
    },
    {
        "name": "find_learning_resources",
        "description": (
            "Find the best courses, tutorials, certifications, and learning paths for a specific skill. "
            "Includes free and paid options with estimated time to proficiency."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "skill": {"type": "string", "description": "Skill to learn (e.g. 'Kubernetes', 'product roadmapping')"},
                "level": {"type": "string", "description": "'beginner', 'intermediate', or 'advanced' (default: intermediate)", "default": "intermediate"}
            },
            "required": ["skill"]
        }
    },
    {
        "name": "get_in_demand_skills",
        "description": (
            "Find the most in-demand and trending skills for a job title right now, "
            "including salary impact and emerging skills to watch."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title": {"type": "string", "description": "Job title to research (e.g. 'DevOps Engineer')"}
            },
            "required": ["job_title"]
        }
    },
    {
        "name": "send_notification",
        "description": "Send yourself a desktop notification and log. Use when you find something important.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title":   {"type": "string", "description": "Notification title"},
                "message": {"type": "string", "description": "Notification body"},
                "priority":{"type": "string", "description": "'normal' or 'urgent'", "default": "normal"}
            },
            "required": ["title", "message"]
        }
    },
    {
        "name": "send_email",
        "description": (
            "Send Anthony an email via Gmail. Use for detailed summaries, job shortlists, "
            "study plans, or anything worth reading later. "
            "Requires Google OAuth setup (python tools/google_tools.py --auth)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "subject":  {"type": "string", "description": "Email subject line"},
                "body":     {"type": "string", "description": "Email body text"},
                "to_email": {"type": "string", "description": "Recipient address (optional, defaults to authorized Gmail)"}
            },
            "required": ["subject", "body"]
        }
    },
    {
        "name": "send_telegram",
        "description": (
            "Send Anthony a Telegram message. Use for brief, urgent alerts — "
            "e.g. a hot job just posted, a trend spike, or a quick reminder. "
            "Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message text (Markdown supported)"}
            },
            "required": ["message"]
        }
    },
    {
        "name": "sheets_create",
        "description": "Create a new Google Sheet and return its URL. Use to start a new job tracker, trend log, or data table.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Name for the new spreadsheet"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "sheets_read",
        "description": "Read rows from a Google Sheet. Provide the spreadsheet ID and optional range like 'Sheet1!A1:E20'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {"type": "string", "description": "The spreadsheet ID from its URL"},
                "range_name":     {"type": "string", "description": "Range to read, e.g. 'Sheet1' or 'Sheet1!A1:E10'", "default": "Sheet1"}
            },
            "required": ["spreadsheet_id"]
        }
    },
    {
        "name": "sheets_write",
        "description": (
            "Write rows to a Google Sheet at a specific range (overwrites). "
            "Use sheets_append to add rows without overwriting."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {"type": "string", "description": "The spreadsheet ID"},
                "range_name":     {"type": "string", "description": "Starting cell, e.g. 'Sheet1!A1'"},
                "values":         {"type": "array",  "items": {"type": "array"}, "description": "2D array of rows and cells"}
            },
            "required": ["spreadsheet_id", "range_name", "values"]
        }
    },
    {
        "name": "sheets_append",
        "description": "Append rows to the end of a Google Sheet without overwriting existing data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spreadsheet_id": {"type": "string", "description": "The spreadsheet ID"},
                "range_name":     {"type": "string", "description": "Sheet name, e.g. 'Sheet1'", "default": "Sheet1"},
                "values":         {"type": "array",  "items": {"type": "array"}, "description": "Rows to append"}
            },
            "required": ["spreadsheet_id", "values"]
        }
    },
    {
        "name": "docs_create",
        "description": (
            "Create a new Google Doc with formatted content. "
            "Use for study plans, research reports, job application drafts, or any document worth keeping."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title":   {"type": "string", "description": "Document title"},
                "content": {"type": "string", "description": "Document body text"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "docs_read",
        "description": "Read the content of an existing Google Doc by its document ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "Google Doc ID from its URL"}
            },
            "required": ["document_id"]
        }
    },
    {
        "name": "drive_list",
        "description": "List files in Google Drive (or a specific folder). Use to check what the agent has already saved.",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder_id":   {"type": "string", "description": "Optional folder ID to list files within"},
                "max_results": {"type": "integer", "description": "Max files to return (default 20)", "default": 20}
            }
        }
    },
    {
        "name": "drive_upload",
        "description": "Upload a text or JSON file directly to Google Drive.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Filename with extension (e.g. 'trends_march.txt')"},
                "content":  {"type": "string", "description": "File content as text"},
                "mimetype": {"type": "string", "description": "'text/plain' or 'application/json'", "default": "text/plain"}
            },
            "required": ["filename", "content"]
        }
    },
    {
        "name": "slides_create",
        "description": "Create a new Google Slides presentation and return its URL. Use for pitch decks, study guides, summaries, or any visual presentation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the presentation"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "slides_read",
        "description": "Read the content and structure of an existing Google Slides presentation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string", "description": "The presentation ID from its URL"}
            },
            "required": ["presentation_id"]
        }
    },
    {
        "name": "slides_add_slide",
        "description": "Add a new slide with a title and body text to an existing presentation. Call repeatedly to build out a full deck.",
        "input_schema": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string", "description": "The presentation ID"},
                "title":           {"type": "string", "description": "Slide title"},
                "body":            {"type": "string", "description": "Slide body text (bullet points separated by newlines)"},
                "notes":           {"type": "string", "description": "Optional speaker notes for this slide"}
            },
            "required": ["presentation_id", "title", "body"]
        }
    },
    {
        "name": "gmail_read_inbox",
        "description": (
            "Read Anthony's Gmail inbox. Returns sender, subject, date, and snippet for recent emails. "
            "Use to check for new messages, job alerts, or anything the user asks about in their email."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Number of emails to return (default 10)", "default": 10},
                "query":       {"type": "string",  "description": "Gmail search filter, e.g. 'is:unread', 'from:recruiter@company.com'. Default: inbox", "default": "in:inbox"}
            }
        }
    },
    {
        "name": "gmail_get_message",
        "description": "Read the full body of a specific email by its ID (from gmail_read_inbox results).",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "The email message ID"}
            },
            "required": ["message_id"]
        }
    },
    {
        "name": "gmail_search",
        "description": (
            "Search Gmail using Gmail's search syntax. "
            "Examples: 'from:recruiter subject:job offer', 'is:unread after:2024/01/01', 'has:attachment'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query":       {"type": "string",  "description": "Gmail search query"},
                "max_results": {"type": "integer", "description": "Max results to return (default 10)", "default": 10}
            },
            "required": ["query"]
        }
    },
    {
        "name": "gmail_mark_read",
        "description": "Mark an email as read.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "The email message ID to mark as read"}
            },
            "required": ["message_id"]
        }
    },
    {
        "name": "save_memory",
        "description": (
            "Persist something you've learned about the user — a preference, a profile fact, or a note. "
            "Call this whenever the user states a preference, goal, constraint, or personal detail "
            "that should be remembered across sessions. "
            "Examples: min salary, preferred locations, target roles, learning style, sector interests."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "'preference' (job/search settings), 'profile' (facts about the user), or 'note' (anything else worth remembering)",
                    "enum": ["preference", "profile", "note"]
                },
                "key":   {"type": "string", "description": "Preference or profile key (e.g. 'min_salary', 'target_role', 'learning_style'). Not needed for notes."},
                "value": {"type": "string", "description": "The value to store"}
            },
            "required": ["type", "value"]
        }
    },
    {
        "name": "parse_job_description",
        "description": (
            "Parse a job description the user pastes and set it as the active learning target. "
            "Call this immediately whenever the user provides a new job description. "
            "Extracts role title, company, required skills, and interview themes, then saves to memory "
            "so all teaching tools automatically use that job's context."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "jd_text": {"type": "string", "description": "The full job description text"}
            },
            "required": ["jd_text"]
        }
    },
    {
        "name": "generate_lesson",
        "description": (
            "Teach a specific sub-topic within a skill area. Returns a conceptual explanation, "
            "runnable Python code example, common gotchas, and next-step suggestions. "
            "Automatically uses the active job target context (set via parse_job_description). "
            "Use whenever the user asks to learn, understand, or practice any technical topic."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic":      {"type": "string", "description": "Specific sub-topic (e.g. 'HNSW index tuning', 'rerankers in RAG')"},
                "skill_area": {"type": "string", "description": "Skill category (e.g. 'Advanced RAG / GraphRAG', 'Embeddings at scale')"},
                "level":      {"type": "string", "description": "'beginner', 'intermediate', or 'advanced'", "default": "intermediate"}
            },
            "required": ["topic", "skill_area"]
        }
    },
    {
        "name": "quiz_me",
        "description": (
            "Generate a mini-quiz on a topic the user has studied. "
            "Returns mixed-type questions: multiple choice, short answer, and code completion. "
            "Use after delivering a lesson or when the user asks to be tested."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic":         {"type": "string", "description": "Topic to quiz on"},
                "skill_area":    {"type": "string", "description": "Skill area context"},
                "num_questions": {"type": "integer", "description": "Number of questions (default 3)", "default": 3}
            },
            "required": ["topic", "skill_area"]
        }
    },
    {
        "name": "update_progress",
        "description": (
            "Record that the user has covered a topic and optionally log a quiz score. "
            "Call after every completed lesson or quiz to track learning progress in memory."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "skill_area": {"type": "string", "description": "Skill area being tracked"},
                "topic":      {"type": "string", "description": "Sub-topic completed"},
                "score":      {"type": "integer", "description": "Quiz score 0-100 (-1 if no quiz)", "default": -1},
                "notes":      {"type": "string", "description": "Optional notes to save", "default": ""}
            },
            "required": ["skill_area", "topic"]
        }
    },
    {
        "name": "get_study_plan",
        "description": (
            "Generate a personalized week-by-week study plan for the active job target. "
            "Uses the user's resume to identify skill gaps and weights the plan accordingly. "
            "Call when the user asks for a study plan, learning roadmap, or curriculum."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "weeks_available":    {"type": "integer", "description": "Weeks until target deadline (default 8)", "default": 8},
                "target_weak_areas":  {"type": "string", "description": "Comma-separated skill areas to prioritize (optional)"}
            },
            "required": []
        }
    }
]

# ── Tool dispatcher ────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict, memory=None) -> str:
    """Execute a tool by name and return result as a string."""

    # Memory tool needs the live memory object — handle before the dispatch table
    if name == "save_memory" and memory is not None:
        kind  = inputs.get("type", "note")
        key   = inputs.get("key", "")
        value = inputs.get("value", "")
        if kind == "preference" and key:
            memory.set_preference(key, value)
        elif kind == "profile" and key:
            memory.update_profile(key, value)
        else:
            memory.add_note(value)
        return json.dumps({"saved": True, "type": kind, "key": key, "value": value})

    dispatch = {
        "search_web":           lambda i: search_web(i["query"], i.get("num_results", 5)),
        "search_jobs":          lambda i: search_jobs(
                                    i["title"],
                                    location=i.get("location"),
                                    min_salary=i.get("min_salary"),
                                    keywords=i.get("keywords", []),
                                    remote=i.get("remote", False)
                                ),
        "get_job_details":      lambda i: get_job_details(i["job_id"]),
        "search_trends":        lambda i: search_trends(i["topic"], i.get("timeframe", "month")),
        "search_business_ideas":lambda i: search_business_ideas(i["area"], i.get("budget", "low")),
        "analyze_skill_gap":    lambda i: analyze_skill_gap(i["job_title"], i["current_skills"]),
        "find_learning_resources": lambda i: find_learning_resources(i["skill"], i.get("level", "intermediate")),
        "get_in_demand_skills": lambda i: get_in_demand_skills(i["job_title"]),
        "save_to_file":         lambda i: save_to_file(i["filename"], i["content"], i.get("format", "md"), i.get("folder", "")),
        "read_file":            lambda i: read_file(i["filename"]),
        "list_saved_files":     lambda i: list_saved_files(),
        "send_notification":      lambda i: send_notification(i["title"], i["message"], i.get("priority", "normal")),
        "send_email":             lambda i: send_email(i["subject"], i["body"], i.get("to_email")),
        "send_telegram":          lambda i: send_telegram(i["message"]),
        "sheets_create":          lambda i: sheets_create(i["title"]),
        "sheets_read":            lambda i: sheets_read(i["spreadsheet_id"], i.get("range_name", "Sheet1")),
        "sheets_write":           lambda i: sheets_write(i["spreadsheet_id"], i["range_name"], i["values"]),
        "sheets_append":          lambda i: sheets_append(i["spreadsheet_id"], i.get("range_name", "Sheet1"), i["values"]),
        "docs_create":            lambda i: docs_create(i["title"], i["content"]),
        "docs_read":              lambda i: docs_read(i["document_id"]),
        "drive_list":             lambda i: drive_list(i.get("folder_id"), i.get("max_results", 20)),
        "drive_upload":           lambda i: drive_upload(i["filename"], i["content"], i.get("mimetype", "text/plain")),
        "slides_create":          lambda i: slides_create(i["title"]),
        "slides_read":            lambda i: slides_read(i["presentation_id"]),
        "slides_add_slide":       lambda i: slides_add_slide(i["presentation_id"], i["title"], i["body"], i.get("notes", "")),
        "gmail_read_inbox":       lambda i: gmail_read_inbox(i.get("max_results", 10), i.get("query", "in:inbox")),
        "gmail_get_message":      lambda i: gmail_get_message(i["message_id"]),
        "gmail_search":           lambda i: gmail_search(i["query"], i.get("max_results", 10)),
        "gmail_mark_read":        lambda i: gmail_mark_read(i["message_id"]),
        "parse_job_description":  lambda i: parse_job_description(i["jd_text"]),
        "generate_lesson":        lambda i: generate_lesson(i["topic"], i["skill_area"], i.get("level", "intermediate")),
        "quiz_me":                lambda i: quiz_me(i["topic"], i["skill_area"], i.get("num_questions", 3)),
        "update_progress":        lambda i: update_progress(i["skill_area"], i["topic"], i.get("score", -1), i.get("notes", "")),
        "get_study_plan":         lambda i: get_study_plan(i.get("weeks_available", 8), i.get("target_weak_areas", "")),
    }
    if name not in dispatch:
        return f"Unknown tool: {name}"
    try:
        result = dispatch[name](inputs)
        return json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
    except Exception as e:
        return f"Tool error: {e}"

# ── Agent loop ─────────────────────────────────────────────────────────────────

def run_agent(user_message: str, memory: Memory) -> str:
    return stream_agent_ollama(user_message, memory, model="gemma4")
    """
    The core agent loop.
    1. Build messages with memory context
    2. Call Claude with tools
    3. If Claude wants to use a tool → run it, add result, loop
    4. Return final text response
    """

    # Pull relevant memory into the system prompt
    memory_context = memory.get_context()

    system_prompt = f"""You are a proactive personal assistant agent. You help with:
- Job research (finding roles, filtering by salary/location/remote, saving lists)
- Business trend analysis (spotting opportunities, emerging niches)
- Skill development (gap analysis, learning resources, in-demand skill research)
- Personal assistant tasks (reminders, notes, research, summaries)

You have tools available. When given a task, use them proactively — don't just answer
from memory. Search, verify, and save results when useful.

When you find jobs or trends the user would care about, save them to a file automatically.
When you find something urgent or exceptional, send a notification.

Always be specific: include salaries, company names, dates, and links when available.

When analyzing skill gaps or recommending learning resources, use the user's resume below
as the baseline for their current skills — don't ask them to list skills unless they want
to override the resume.

## User's Resume:
{RESUME_TEXT}

## What I know about this user:
{memory_context}

## Teaching Mode
You are also a technical mentor. You adapt to whatever job the user is targeting
(active job target shown above; defaults to Wells Fargo AI Engineer if none set).

When the user pastes a job description → call parse_job_description immediately.
When the user asks to learn, study, or practice any topic:
1. Call generate_lesson (auto-uses active job context).
2. After the lesson, offer to quiz them via quiz_me.
3. After a quiz, call update_progress to record topic + score.
4. For a study plan, call get_study_plan (run analyze_skill_gap first if helpful).
"""

    messages = memory.get_recent_messages() + [{"role": "user", "content": user_message}]

    print(f"\n🤖 Agent thinking...\n")

    # Agentic loop — keeps going until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="gemma4",
            max_tokens=8096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # Add assistant response to message history
        messages.append({"role": "assistant", "content": response.content})

        # Check if Claude wants to use tools
        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if not tool_calls:
            # No more tool calls — we're done
            final_text = " ".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            memory.add_exchange(user_message, final_text)
            return final_text

        # Execute every tool Claude requested
        tool_results = []
        for tool_call in tool_calls:
            print(f"  🔧 Using tool: {tool_call.name}({json.dumps(tool_call.input, separators=(',',':'))})")
            result = run_tool(tool_call.name, tool_call.input, memory)
            print(f"  ✅ Done\n")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            })

        # Feed results back to Claude and loop
        messages.append({"role": "user", "content": tool_results})

# ── Streaming agent loop (for web UI) ─────────────────────────────────────────

# ── Ollama fallback agent ──────────────────────────────────────────────────────

# Tools safe for smaller local models — excludes complex nested-array schemas
# that confuse llama3.2 and similar models.
OLLAMA_TOOLS = [t for t in TOOLS if t["name"] in {
    "search_web", "search_jobs", "search_trends", "search_business_ideas",
    "save_to_file", "read_file", "list_saved_files",
    "send_notification", "send_email", "send_telegram",
    "save_memory", "analyze_skill_gap", "find_learning_resources",
    "get_in_demand_skills", "gmail_read_inbox", "gmail_get_message",
    "gmail_search", "gmail_mark_read",
}]


def _anthropic_tools_to_openai(tools: list) -> list:
    """Convert Anthropic tool definitions to OpenAI/Ollama function-calling format."""
    result = []
    for t in tools:
        schema = t.get("input_schema", {"type": "object", "properties": {}})
        # Remove "default" from property definitions — some Ollama models reject them
        props = {}
        for k, v in schema.get("properties", {}).items():
            props[k] = {pk: pv for pk, pv in v.items() if pk != "default"}
        clean_schema = {"type": "object", "properties": props}
        if schema.get("required"):
            clean_schema["required"] = schema["required"]
        result.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", "")[:200],  # cap length
                "parameters": clean_schema,
            },
        })
    return result


def stream_agent_ollama(user_message: str, memory: Memory, model: str = None):
    """
    Fallback agent loop using Ollama via its OpenAI-compatible API.
    Yields the same SSE event format as stream_agent so the frontend is unchanged.
    """
    from openai import OpenAI as OllamaClient
    from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_FALLBACK_MODELS

    chosen_model = model or OLLAMA_MODEL
    ol_tools = _anthropic_tools_to_openai(OLLAMA_TOOLS)
    memory_context = memory.get_context()

    system_prompt = f"""You are a proactive personal assistant agent for Anthony Joyner.
You help with job research, business trends, skill development, and personal assistant tasks.
Use the available tools when needed. Be specific with salaries, company names, and dates.

## User's Resume:
{RESUME_TEXT}

## What I know about this user:
{memory_context}

Note: You are running on a local Ollama model ({chosen_model}) as a fallback.
"""

    user_content = user_message if isinstance(user_message, list) else user_message
    messages = [{"role": "system", "content": system_prompt}]
    for ex in memory.get_recent_messages():
        messages.append(ex)
    messages.append({"role": "user", "content": user_content if isinstance(user_content, str) else "[attachment]"})

    models_to_try = [chosen_model] + [m for m in OLLAMA_FALLBACK_MODELS if m != chosen_model]
    client = OllamaClient(base_url=OLLAMA_BASE_URL, api_key="ollama")

    last_error = None
    for attempt_model in models_to_try:
        try:
            yield f"data: {json.dumps({'type': 'text', 'content': f'_(Using local Ollama model: {attempt_model})_'})}\n\n"

            current_messages = list(messages)
            while True:
                response = client.chat.completions.create(
                    model=attempt_model,
                    messages=current_messages,
                    tools=ol_tools,
                    tool_choice="auto",
                )
                msg = response.choices[0].message

                # Serialize tool_calls to plain dicts — SDK objects break on resend
                tc_list = msg.tool_calls or []
                tc_dicts = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tc_list
                ]
                assistant_msg = {"role": "assistant", "content": msg.content or ""}
                if tc_dicts:
                    assistant_msg["tool_calls"] = tc_dicts
                current_messages.append(assistant_msg)

                if not tc_list:
                    final_text = msg.content or ""
                    history_msg = user_message if isinstance(user_message, str) else "[attachment]"
                    memory.add_exchange(history_msg, final_text)
                    yield f"data: {json.dumps({'type': 'text', 'content': final_text})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return

                for tc, tc_dict in zip(tc_list, tc_dicts):
                    name = tc.function.name
                    try:
                        inputs = json.loads(tc.function.arguments or "{}")
                    except Exception:
                        inputs = {}
                    yield f"data: {json.dumps({'type': 'tool', 'name': name, 'input': inputs})}\n\n"
                    result = run_tool(name, inputs, memory)
                    yield f"data: {json.dumps({'type': 'result', 'name': name})}\n\n"
                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tc_dict["id"],
                        "content": result,
                    })
            return  # success — don't try next model

        except Exception as e:
            last_error = str(e)
            if "connection" in last_error.lower() or "refused" in last_error.lower():
                yield f"data: {json.dumps({'type': 'text', 'content': '⚠️ Ollama is not running. Start it with `ollama serve` then try again.'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            continue  # try next model

    yield f"data: {json.dumps({'type': 'text', 'content': f'All Ollama models failed. Last error: {last_error}'})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


def stream_agent(user_message: str, memory: Memory):
    """
    Generator version of run_agent for Server-Sent Events streaming.
    Yields SSE-formatted strings so the web UI can show tool calls in real-time.

    Event types:
      {"type": "tool",   "name": "...", "input": {...}}   — tool starting
      {"type": "result", "name": "..."}                   — tool finished
      {"type": "text",   "content": "..."}                — final response
      {"type": "done"}                                     — stream complete
    """
    memory_context = memory.get_context()

    system_prompt = f"""You are a proactive personal assistant agent. You help with:
- Job research (finding roles, filtering by salary/location/remote, saving lists)
- Business trend analysis (spotting opportunities, emerging niches)
- Skill development (gap analysis, learning resources, in-demand skill research)
- Personal assistant tasks (reminders, notes, research, summaries)

You have tools available. When given a task, use them proactively — don't just answer
from memory. Search, verify, and save results when useful.

When you find jobs or trends the user would care about, save them to a file automatically.
When you find something urgent or exceptional, send a notification.

Always be specific: include salaries, company names, dates, and links when available.

When analyzing skill gaps or recommending learning resources, use the user's resume below
as the baseline for their current skills — don't ask them to list skills unless they want
to override the resume.

## User's Resume:
{RESUME_TEXT}

## What I know about this user:
{memory_context}

## Teaching Mode
You are also a technical mentor. You adapt to whatever job the user is targeting
(active job target shown above; defaults to Wells Fargo AI Engineer if none set).

When the user pastes a job description → call parse_job_description immediately.
When the user asks to learn, study, or practice any topic:
1. Call generate_lesson (auto-uses active job context).
2. After the lesson, offer to quiz them via quiz_me.
3. After a quiz, call update_progress to record topic + score.
4. For a study plan, call get_study_plan (run analyze_skill_gap first if helpful).
"""

    # user_message may be a plain string or a list of content blocks (vision)
    user_content = user_message if isinstance(user_message, list) else user_message
    messages = memory.get_recent_messages() + [{"role": "user", "content": user_content}]

    while True:
        response = client.messages.create(
            model="gemma4",
            max_tokens=8096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.content})
        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if not tool_calls:
            final_text = " ".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            # Store plain text in history even if original message was content blocks
            history_msg = user_message if isinstance(user_message, str) else "[attachment]"
            memory.add_exchange(history_msg, final_text)
            yield f"data: {json.dumps({'type': 'text', 'content': final_text})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        tool_results = []
        for tool_call in tool_calls:
            yield f"data: {json.dumps({'type': 'tool', 'name': tool_call.name, 'input': tool_call.input})}\n\n"
            result = run_tool(tool_call.name, tool_call.input, memory)
            yield f"data: {json.dumps({'type': 'result', 'name': tool_call.name})}\n\n"
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            })

        messages.append({"role": "user", "content": tool_results})


# ── Interactive CLI ────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Personal Assistant Agent")
    parser.add_argument("--voice", action="store_true",
                        help="Enable voice mode: speak your input, hear the response")
    parser.add_argument("--voice-model", default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size for transcription (default: base)")
    args = parser.parse_args()

    voice_mode = args.voice
    if voice_mode:
        from tools.voice import speak, record_and_transcribe

    memory = Memory()

    print("=" * 60)
    print("  Personal Assistant Agent" + (" 🎙  [Voice Mode]" if voice_mode else ""))
    print("  Type 'quit' to exit | 'memory' to see what I know")
    if voice_mode:
        print("  Press Enter to start speaking, Enter again to stop.")
    print("=" * 60)
    print("\nExamples:")
    print("  • Find remote marketing jobs paying over 80k")
    print("  • What are the hottest business trends right now?")
    print("  • Teach me RAG chunking strategies")
    print("  • Quiz me on vector database indexing")
    print("  • Build me an 8-week study plan for the Wells Fargo AI Engineer role")
    print("  • [paste any job description] to set a new learning target")
    print()

    while True:
        try:
            if voice_mode:
                print("You (press Enter to speak): ", end="", flush=True)
                input()  # wait for Enter before recording
                user_input = record_and_transcribe(
                    prompt_text="Recording... press Enter to stop.",
                    model_name=args.voice_model,
                )
                if not user_input:
                    continue
            else:
                user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if user_input.lower() == "memory":
            print("\n📧 Memory context:\n" + memory.get_context())
            continue

        response = run_agent(user_input, memory)
        print(f"\nAgent: {response}\n")

        if voice_mode:
            speak(response)

        print("-" * 60)

if __name__ == "__main__":
    main()
