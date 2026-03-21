import os
import re
from pathlib import Path


def create_messages(user_inputs: list) -> list:
    """
    Creates a message structure for chat conversations.
    
    Takes user input as an array and appends it to the message structure.
    
    Args:
        user_inputs: List of user input messages to append
        
    Returns:
        List of message dictionaries with role and content
    """
    # Start with system message (empty for now)
    messages = [
        {
            "role": "system",
            "content": ""
        }
    ]
    
    # Append user inputs to the messages
    for user_input in user_inputs:
        messages.append({
            "role": "user",
            "content": user_input
        })
    
    return messages


def create_example_messages(example_description: str, file_content: str) -> list:
    """
    Creates a message structure with system, user (explanation), and assistant (content) messages.
    
    Args:
        example_description: Description of what the example does
        file_content: Content of the file (assistant response)
        
    Returns:
        List of message dictionaries with system, user, and assistant roles
    """
    return [
        {
            "role": "system",
            "content": ""
        },
        {
            "role": "user",
            "content": example_description
        },
        {
            "role": "assistant",
            "content": file_content
        }
    ]


def create_messages_from_examples(examples_dir: str, descriptions: dict = None) -> list:
    """
    Loops through the examples directory and creates messages for each example file.
    
    Args:
        examples_dir: Path to the examples directory
        descriptions: Optional dictionary mapping file names to descriptions
        
    Returns:
        List of message lists, one for each example file
    """
    all_messages = []
    
    # Ensure the directory exists
    if not os.path.exists(examples_dir):
        raise FileNotFoundError(f"Examples directory not found: {examples_dir}")
    
    # Get all Python files in the directory
    example_files = sorted([f for f in os.listdir(examples_dir) if f.endswith('.py')])
    
    for filename in example_files:
        filepath = os.path.join(examples_dir, filename)
        
        try:
            # Read the file content
            with open(filepath, 'r', encoding='utf-8') as file:
                file_content = file.read()
            
            # Get description from the provided dict or generate a default one
            if descriptions and filename in descriptions:
                description = descriptions[filename]
            else:
                # Generate a default description from the filename
                description = f"Explain what the {filename} example does"
            
            # Create the message structure for this example
            messages = create_example_messages(description, file_content)
            all_messages.append({
                "filename": filename,
                "messages": messages
            })
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    return all_messages


def extract_scenes_from_file(file_path: str) -> list:
    """
    Extracts individual scene classes from a Python file containing multiple scenes.
    
    Args:
        file_path: Path to the Python file containing multiple scene classes
        
    Returns:
        List of dictionaries containing scene names and their code
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Pattern to match class definitions
    class_pattern = r'(class\s+(\w+)\(Scene\):\s*(?:""".*?"""|\'\'\'.*?\'\'\')?.*?)(?=class\s+\w+\(Scene\)|$)'
    
    matches = re.finditer(class_pattern, file_content, re.DOTALL)
    scenes = []
    
    for match in matches:
        scene_code = match.group(1).strip()
        scene_name = match.group(2)
        
        scenes.append({
            "name": scene_name,
            "code": scene_code,
            "description": f"Scene: {scene_name}"
        })
    
    return scenes


def create_messages_for_multi_scene_file(file_path: str, user_prompt: str = None) -> dict:
    """
    Creates message structures for a file containing multiple scenes.
    
    Args:
        file_path: Path to the Python file with multiple scenes
        user_prompt: Optional user prompt explaining what the scenes do
        
    Returns:
        Dictionary containing overall file info and individual scene messages
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    scenes = extract_scenes_from_file(file_path)
    
    result = {
        "file": os.path.basename(file_path),
        "full_content": full_content,
        "scenes": [],
        "overall_messages": [
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": user_prompt or f"Explain what the scenes in {os.path.basename(file_path)} do"
            },
            {
                "role": "assistant",
                "content": full_content
            }
        ]
    }
    
    # Create messages for each individual scene
    for scene in scenes:
        scene_messages = [
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": f"Explain what the {scene['name']} scene does"
            },
            {
                "role": "assistant",
                "content": scene['code']
            }
        ]
        
        result["scenes"].append({
            "name": scene['name'],
            "messages": scene_messages
        })
    
    return result
