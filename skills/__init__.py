import os
import importlib
import logging

logger = logging.getLogger(__name__)

def load_skills():
    """Dynamically loads all skill modules in the skills/ directory."""
    skills = []
    skills_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(skills_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"skills.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                # Verify it has the required interface
                if hasattr(module, "get_tools") and hasattr(module, "handle_tool"):
                    skills.append(module)
                    logger.info(f"Skill loaded: {module_name}")
                else:
                    logger.warning(f"Skipping module {module_name}: Missing required functions.")
            except Exception as e:
                logger.error(f"Failed to load skill {module_name}: {e}")
                
    return skills
