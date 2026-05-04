import os
import json
import logging
from datetime import datetime
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL
from memory.memory import Memory

logger = logging.getLogger(__name__)

class SpecKitSkill:
    """
    Skill that enables the agent to natively execute Spec-Kit methodology commands.
    It reads .toml command definitions from .gemini/commands and structures 
    responses based on project templates.
    """
    
    def __init__(self):
        self.commands_dir = "/Users/anthonyjoyner/Documents/Projects/my_agent/.gemini/commands"
        self.specs_dir = "/Users/anthonyjoyner/Documents/Projects/my_agent/specs"
        self.templates_dir = "/Users/anthonyjoyner/Documents/Projects/my_agent/.specify/templates"

    def get_tools(self):
        return [
            {
                "name": "speckit_specify",
                "description": "Starts the SDD process by creating a new feature specification.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "description": "Natural language description of the feature to build."}
                    },
                    "required": ["description"]
                }
            },
            {
                "name": "speckit_plan",
                "description": "Generates a technical implementation plan for the current feature.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tech_stack": {"type": "string", "description": "The desired technology stack (e.g., Python, SQLite, React)."}
                    },
                    "required": ["tech_stack"]
                }
            },
            {
                "name": "speckit_tasks",
                "description": "Breaks the implementation plan into actionable technical tasks.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def _get_next_feature_num(self):
        """Finds the next available 3-digit number for sequential feature numbering."""
        if not os.path.exists(self.specs_dir):
            return "001"
        existing = [d for d in os.listdir(self.specs_dir) if os.path.isdir(os.path.join(self.specs_dir, d))]
        nums = []
        for d in existing:
            if d[:3].isdigit():
                nums.append(int(d[:3]))
        return f"{max(nums or [0]) + 1:03d}"

    def handle_tool(self, name, inputs, memory):
        if name == "speckit_specify":
            return self._specify(inputs["description"], memory)
        if name == "speckit_plan":
            return self._plan(inputs["tech_stack"], memory)
        if name == "speckit_tasks":
            return self._tasks(memory)
        return None

    def _tasks(self, memory):
        """Implements the logic from speckit.tasks.toml."""
        # Load the current feature directory
        feature_json_path = "/Users/anthonyjoyner/Documents/Projects/my_agent/.specify/feature.json"
        if not os.path.exists(feature_json_path):
            return "Error: No active feature found. Run speckit_specify first."
            
        with open(feature_json_path, "r") as f:
            feature_data = json.load(f)
            
        feature_dir_path = feature_data["feature_directory"]
        abs_feature_dir = os.path.join("/Users/anthonyjoyner/Documents/Projects/my_agent", feature_dir_path)
        
        # Read template and write initial tasks.md
        template_path = os.path.join(self.templates_dir, "tasks-template.md")
        tasks_file = os.path.join(abs_feature_dir, "tasks.md")
        
        content = ""
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                content = f.read()
            
            # Simple placeholder replacement
            content = content.replace("[FEATURE NAME]", feature_dir_path.split("-", 1)[-1].replace("-", " ").title())
            content = content.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))

        with open(tasks_file, "w") as f:
            f.write(content)
            
        return json.dumps({
            "status": "Success",
            "message": f"Task backlog created at {tasks_file}. I will now populate it based on the plan.md.",
            "tasks_file": tasks_file
        })

    def _specify(self, description, memory):
        """Implements the logic from speckit.specify.toml."""
        # 1. Generate short name
        short_name = description.lower().replace(" ", "-")[:30].strip("-")
        feature_num = self._get_next_feature_num()
        feature_dir_name = f"{feature_num}-{short_name}"
        feature_dir = os.path.join(self.specs_dir, feature_dir_name)
        
        # 2. Create directory structure
        os.makedirs(feature_dir, exist_ok=True)
        os.makedirs(os.path.join(feature_dir, "checklists"), exist_ok=True)
        
        # 3. Read template and write initial spec.md
        template_path = os.path.join(self.templates_dir, "spec-template.md")
        spec_file = os.path.join(feature_dir, "spec.md")
        
        content = ""
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                content = f.read()
            
            # Simple placeholder replacement
            content = content.replace("[FEATURE NAME]", short_name.replace("-", " ").title())
            content = content.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
            content = content.replace("$ARGUMENTS", description)
        
        with open(spec_file, "w") as f:
            f.write(content)
        
        # 4. Save feature context
        with open("/Users/anthonyjoyner/Documents/Projects/my_agent/.specify/feature.json", "w") as f:
            json.dump({"feature_directory": f"specs/{feature_dir_name}"}, f)
            
        return json.dumps({
            "status": "Success",
            "message": f"Feature directory and initial spec.md created at {feature_dir}.",
            "spec_file": spec_file,
            "feature_num": feature_num
        })

    def _plan(self, tech_stack, memory):
        """Implements the logic from speckit.plan.toml."""
        # Load the current feature directory
        feature_json_path = "/Users/anthonyjoyner/Documents/Projects/my_agent/.specify/feature.json"
        if not os.path.exists(feature_json_path):
            return "Error: No active feature found. Run speckit_specify first."
            
        with open(feature_json_path, "r") as f:
            feature_data = json.load(f)
            
        feature_dir_path = feature_data["feature_directory"]
        abs_feature_dir = os.path.join("/Users/anthonyjoyner/Documents/Projects/my_agent", feature_dir_path)
        
        # Read template and write initial plan.md
        template_path = os.path.join(self.templates_dir, "plan-template.md")
        plan_file = os.path.join(abs_feature_dir, "plan.md")
        
        content = ""
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                content = f.read()
            
            # Simple placeholder replacement
            content = content.replace("[FEATURE]", feature_dir_path.split("-", 1)[-1].replace("-", " ").title())
            content = content.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
            content = content.replace("[e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]", tech_stack)

        with open(plan_file, "w") as f:
            f.write(content)
            
        return json.dumps({
            "status": "Success",
            "message": f"Implementation plan created at {plan_file}. Please refine the plan now.",
            "plan_file": plan_file,
            "tech_stack": tech_stack
        })

    def get_system_prompt(self):
        return (
            "You are the Lead Software Engineer implementing the 'Specify' methodology. "
            "Always follow the SDD workflow: Specify -> Plan -> Tasks -> Implement. "
            "Maintain the project Constitution and ensure all features are documented in the 'specs/' directory."
        )

# Instantiate the skill
speckit_skill = SpecKitSkill()

def get_tools():
    return speckit_skill.get_tools()

def handle_tool(name, inputs, memory):
    return speckit_skill.handle_tool(name, inputs, memory)

def get_system_prompt():
    return speckit_skill.get_system_prompt()
