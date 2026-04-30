import os
import re

def migrate_agent_py():
    with open('agent.py', 'r') as f:
        content = f.read()
    
    # Ensure import anthropic is gone (already done by sed, but double check)
    content = re.sub(r'^import anthropic\n', '', content, flags=re.MULTILINE)
    
    # Update stream_agent_ollama to use gemma4 model
    # It might be using a variable or a hardcoded string. 
    # Let's look for model assignment.
    content = re.sub(r'model\s*=\s*["\'][^"\']+["\']', 'model="gemma4"', content)
    
    # Replace stream_agent body to call stream_agent_ollama
    pattern = r'def stream_agent\(user_message: str, memory: Memory\) -> str:.*?(?=\ndef|$)'
    replacement = 'def stream_agent(user_message: str, memory: Memory) -> str:\n    return stream_agent_ollama(user_message, memory)'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('agent.py', 'w') as f:
        f.write(content)

def migrate_tools():
    tools_dir = 'tools'
    if os.path.exists(tools_dir):
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py'):
                path = os.path.join(tools_dir, filename)
                with open(path, 'r') as f:
                    lines = f.readlines()
                with open(path, 'w') as f:
                    for line in lines:
                        if 'import anthropic' in line or 'anthropic.Anthropic' in line:
                            continue
                        f.write(line)

migrate_agent_py()
migrate_tools()
print("Migration completed.")
