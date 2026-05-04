import json
import os
from datetime import datetime
from sqlmodel import Session, select
from skills.dashboard import engine, SkillLog, InterviewHistory
from tools.client import client
from config.settings import RESUME_TEXT

def get_tools():
    return [
        {
            "name": "generate_mock_interview",
            "description": "Generates 5 tailored interview questions based on trending skills from the dashboard.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string", "description": "The job title to practice for."}
                },
                "required": ["job_title"]
            }
        },
        {
            "name": "score_interview_answer",
            "description": "Scores a specific interview answer against the user's resume and provides feedback.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The interview question asked."},
                    "answer": {"type": "string", "description": "The user's spoken or typed answer."}
                },
                "required": ["question", "answer"]
            }
        }
    ]

def handle_tool(name, inputs, memory):
    if name == "generate_mock_interview":
        return generate_interview(inputs["job_title"])
    if name == "score_interview_answer":
        return score_answer(inputs["question"], inputs["answer"])
    return None

def get_trending_skills():
    """Queries the database for the top skills."""
    from collections import Counter
    with Session(engine) as session:
        statement = select(SkillLog.skill_name)
        results = session.exec(statement).all()
        counts = Counter(results)
        return [skill for skill, _ in counts.most_common(5)]

def generate_interview(job_title):
    skills = get_trending_skills()
    skills_str = ", ".join(skills) if skills else "General Enterprise Software"
    
    prompt = f"""
    Generate 5 interview questions for a {job_title} role.
    Focus on these trending skills: {skills_str}.
    Mix technical and behavioral questions.
    Return ONLY a JSON list of strings.
    """
    
    response = client.messages.create(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        text = response.content[0].text
        # Clean potential markdown
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        elif "```" in text: text = text.split("```")[1].split("```")[0]
        
        questions = json.loads(text.strip())
        
        # Save to history
        with Session(engine) as session:
            history = InterviewHistory(
                job_title=job_title,
                questions_json=json.dumps(questions)
            )
            session.add(history)
            session.commit()
            
        return json.dumps({
            "status": "Ready",
            "message": f"I've generated a mock interview for {job_title}. Should we start? I'll read the first question.",
            "questions": questions
        })
    except Exception as e:
        return f"Error generating interview: {e}"

def score_answer(question, answer):
    prompt = f"""
    Resume Context:
    {RESUME_TEXT}
    
    Question: {question}
    User Answer: {answer}
    
    Score this answer from 1-10. Provide 2 sentences of feedback.
    Return JSON format: {{"score": 8, "feedback": "..."}}
    """
    
    response = client.messages.create(
        model="gemma4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        text = response.content[0].text
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        return text.strip()
    except:
        return "Error scoring answer."

def get_system_prompt():
    return "You have the 'Interview Preparation' skill. You can generate mock interviews and score the user's verbal or typed responses."
