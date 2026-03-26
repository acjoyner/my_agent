"""
Personal Assistant Agent
========================
Researches jobs, business trends, and handles personal assistant tasks.
Run: python agent.py
"""

from dotenv import load_dotenv
load_dotenv()

import anthropic
import json
from tools.web_search   import search_web
from tools.job_search   import search_jobs, get_job_details
from tools.trends       import search_trends, search_business_ideas
from tools.skills       import analyze_skill_gap, find_learning_resources, get_in_demand_skills
from tools.teach        import generate_lesson, quiz_me, update_progress, get_study_plan, parse_job_description
from tools.file_tools   import save_to_file, read_file, list_saved_files
from tools.notify       import send_notification
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
        "description": "Send yourself a notification (desktop alert or log). Use when you find something important.",
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

def run_tool(name: str, inputs: dict) -> str:
    """Execute a tool by name and return result as a string."""
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
    """
    The core agent loop.
    1. Build messages with memory context
    2. Call Claude with tools
    3. If Claude wants to use a tool → run it, add result, loop
    4. Return final text response
    """
    client = anthropic.Anthropic()

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
            model="claude-opus-4-5",
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
            result = run_tool(tool_call.name, tool_call.input)
            print(f"  ✅ Done\n")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            })

        # Feed results back to Claude and loop
        messages.append({"role": "user", "content": tool_results})

# ── Streaming agent loop (for web UI) ─────────────────────────────────────────

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
    client = anthropic.Anthropic()
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

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
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
            memory.add_exchange(user_message, final_text)
            yield f"data: {json.dumps({'type': 'text', 'content': final_text})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        tool_results = []
        for tool_call in tool_calls:
            yield f"data: {json.dumps({'type': 'tool', 'name': tool_call.name, 'input': tool_call.input})}\n\n"
            result = run_tool(tool_call.name, tool_call.input)
            yield f"data: {json.dumps({'type': 'result', 'name': tool_call.name})}\n\n"
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            })

        messages.append({"role": "user", "content": tool_results})


# ── Interactive CLI ────────────────────────────────────────────────────────────

def main():
    memory = Memory()

    print("=" * 60)
    print("  Personal Assistant Agent")
    print("  Type 'quit' to exit | 'memory' to see what I know")
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
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "memory":
            print("\n📧 Memory context:\n" + memory.get_context())
            continue

        response = run_agent(user_input, memory)
        print(f"\nAgent: {response}\n")
        print("-" * 60)

if __name__ == "__main__":
    main()
