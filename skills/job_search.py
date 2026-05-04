import json
from tools.job_search import search_jobs
from tools.skills import analyze_skill_gap

def get_tools():
    return [
        {"name": "search_jobs", "description": "Search for job listings.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "location": {"type": "string"}}, "required": ["title"]}},
        {"name": "analyze_skill_gap", "description": "Compare skills against a target job.", "input_schema": {"type": "object", "properties": {"job_title": {"type": "string"}, "current_skills": {"type": "string"}}, "required": ["job_title", "current_skills"]}}
    ]

def handle_tool(name, inputs, memory):
    if name == "search_jobs":
        return json.dumps(search_jobs(inputs["title"], location=inputs.get("location")))
    if name == "analyze_skill_gap":
        return json.dumps(analyze_skill_gap(inputs["job_title"], inputs["current_skills"]))
    return None

def get_system_prompt():
    return "You have the 'Job Search' skill. Use it to find roles and analyze skill gaps based on the user's resume."
