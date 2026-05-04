import os
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, create_engine

# --- Standard Skill Interface Requirements ---

def get_tools():
    """Tells agent.py what this skill can do."""
    return [
        {
            "name": "view_dashboard_status",
            "description": "Returns the URL and status of the personal dashboard.",
            "input_schema": {"type": "object", "properties": {}}
        }
    ]

def handle_tool(name, inputs, memory):
    """Standard entry point for your modular skill architecture."""
    if name == "view_dashboard_status":
        return json.dumps({"status": "online", "url": "http://localhost:8000/dashboard/"})
    return None

# --- Dashboard Logic ---

sqlite_file_name = "dashboard.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

class WidgetSetting(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    widget_type: str
    is_active: bool = True

class SkillLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    skill_name: str = Field(index=True)
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)

class InterviewHistory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    job_title: str
    questions_json: str # Store as JSON string
    answers_json: str = "{}"
    score: float = 0.0
    feedback: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

def init_db():
    SQLModel.metadata.create_all(engine)

def log_skills(skill_list: list, source: str):
    """Persists a list of skills to the database."""
    from sqlmodel import Session
    with Session(engine) as session:
        for skill in skill_list:
            log_entry = SkillLog(skill_name=skill, source=source)
            session.add(log_entry)
        session.commit()

# Note: If your app.py mounts skills as sub-apps, it needs this 'app' object
app = FastAPI()

# Mount the static files for the dashboard UI (T002)
# Access at /dashboard/static/...
app.mount("/static", StaticFiles(directory="static/dashboard"), name="dashboard_static")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
async def dashboard_root():
    """Serves the main dashboard HTML."""
    from fastapi.responses import FileResponse
    return FileResponse("static/dashboard/index.html")

@app.get("/jobs")
async def get_recent_jobs():
    """Reads processed job listings from the local output directory."""
    # Use relative path from project root
    output_path = "output"
    jobs_data = []
    
    if os.path.exists(output_path):
        # Look for JSON result files recursively in output/
        for root, _, files in os.walk(output_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        try:
                            data = json.load(f)
                            # Handle different JSON structures safely
                            if isinstance(data, dict) and "jobs" in data:
                                # This is a job search result file
                                for j in data["jobs"][:3]:
                                    jobs_data.append({"source": file, "content": j})
                            else:
                                # This might be a single job or other data
                                jobs_data.append({"source": file, "content": data})
                        except:
                            continue
                    if len(jobs_data) >= 10: break
            if len(jobs_data) >= 10: break
                    
    return {"jobs": jobs_data}

@app.get("/skills")
async def get_recent_skills():
    """Reads processed skill gap reports."""
    path = "output/skills"
    skills_data = []
    if os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.json')]
        for file in files[:3]:
            with open(os.path.join(path, file), 'r') as f:
                try:
                    skills_data.append(json.load(f))
                except: continue
    return {"skills": skills_data}

@app.get("/notifications")
async def get_notifications():
    """Reads recent notifications from the log file."""
    path = "output/notifications.log"
    notifications = []
    if os.path.exists(path):
        with open(path, 'r') as f:
            # Get last 5 lines
            lines = f.readlines()[-5:]
            for line in lines:
                if "]" in line:
                    parts = line.split("]", 1)
                    notifications.append({
                        "timestamp": parts[0].strip("["),
                        "message": parts[1].strip()
                    })
    return {"notifications": notifications[::-1]} # Newest first

@app.get("/analytics/skills")
async def get_skill_analytics():
    """Aggregates skills from output files and database to identify trends."""
    from collections import Counter
    skill_counts = Counter()
    
    # 1. Scan output/skills for recent reports
    skills_path = "output/skills"
    if os.path.exists(skills_path):
        for file in os.listdir(skills_path):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(skills_path, file), 'r') as f:
                        data = json.load(f)
                        # Count missing skills (the "Trending" ones to learn)
                        for s in data.get("missing_skills", []):
                            skill_counts[s] += 1
                        # Count matched skills (the ones user has)
                        for s in data.get("matched_skills", []):
                            skill_counts[s] += 1
                except: continue

    # 2. Extract Top 10
    top_skills = [{"name": name, "count": count} for name, count in skill_counts.most_common(10)]
    
    return {"trending_skills": top_skills}

@app.get("/interviews")
async def get_interview_history():
    """Reads recent mock interview results from the database."""
    from sqlmodel import Session, select
    with Session(engine) as session:
        statement = select(InterviewHistory).order_by(InterviewHistory.timestamp.desc()).limit(5)
        results = session.exec(statement).all()
        return {"interviews": [r.dict() for r in results]}
