import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

# --- Standard Skill Interface Requirements ---

def get_tools():
    return [
        {
            "name": "git_status",
            "description": "Shows the current status of the git repository.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "The path to the local git repository."}
                },
                "required": ["repo_path"]
            }
        },
        {
            "name": "git_commit_and_push",
            "description": "Stages all changes, commits them with a message, and pushes to the current branch.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "The path to the local git repository."},
                    "message": {"type": "string", "description": "The commit message."}
                },
                "required": ["repo_path", "message"]
            }
        },
        {
            "name": "github_create_repo",
            "description": "Creates a new repository on GitHub (requires environment variable GITHUB_TOKEN).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the new repository."},
                    "description": {"type": "string", "description": "Optional description for the repository."}
                },
                "required": ["name"]
            }
        }
    ]

def handle_tool(name, inputs, memory):
    if name == "git_status":
        return run_git_command(inputs["repo_path"], "git status")
    if name == "git_commit_and_push":
        return git_commit_and_push(inputs["repo_path"], inputs["message"])
    if name == "github_create_repo":
        return github_create_repo(inputs["name"], inputs.get("description", ""))
    return None

# --- Core Logic ---

def run_git_command(repo_path, command):
    """Executes a git command in the specified directory."""
    try:
        # Resolve absolute path
        abs_path = os.path.abspath(repo_path)
        if not os.path.exists(abs_path):
            return f"Error: Path {abs_path} does not exist."
            
        result = subprocess.check_output(command, shell=True, cwd=abs_path, stderr=subprocess.STDOUT)
        return result.decode() if result else "Success (no output)"
    except subprocess.CalledProcessError as e:
        output = e.output.decode() if e.output else "No error output provided"
        return f"Git Error: {output}"
    except Exception as e:
        return f"System Error: {str(e)}"

def git_commit_and_push(repo_path, message):
    """Stages, commits, and pushes changes."""
    try:
        abs_path = os.path.abspath(repo_path)
        # Stage all changes
        subprocess.check_call("git add .", shell=True, cwd=abs_path)
        # Commit
        subprocess.check_call(f'git commit -m "{message}"', shell=True, cwd=abs_path)
        # Push
        result = subprocess.check_output("git push", shell=True, cwd=abs_path, stderr=subprocess.STDOUT)
        
        output = result.decode() if result else "Done"
        return json.dumps({
            "status": "Success",
            "message": f"Changes committed and pushed to GitHub.",
            "output": output
        })
    except subprocess.CalledProcessError as e:
        output = e.output.decode() if e.output else "No error output provided"
        return f"Git Error: {output}"
    except Exception as e:
        return f"System Error: {str(e)}"

def github_create_repo(name, description=""):
    """Creates a repository using the GitHub API."""
    from github import Github
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
    if not token:
        return "Error: GITHUB_TOKEN environment variable not set."
        
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.create_repo(name=name, description=description)
        return json.dumps({
            "status": "Success",
            "message": f"Repository '{name}' created successfully.",
            "url": repo.html_url
        })
    except Exception as e:
        return f"GitHub API Error: {str(e)}"

def get_system_prompt():
    return "You have the 'GitHub Manager' skill. You can check git status, commit and push changes, and create new repositories on GitHub."
