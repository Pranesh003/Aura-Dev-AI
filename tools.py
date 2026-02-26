import os
from crewai.tools import tool

@tool("write_file_tool")
def write_file_tool(data: str):
    """
    Useful to write code to a file. 
    Input should be exactly in this format: 'filename.py|code_content'
    """
    try:
        if "|" not in data:
            return "Error: Use the format 'filename|content'"
        
        filename, content = data.split("|", 1)
        filename = filename.strip()
        
        # Sanitize filename for Windows
        import re
        filename = filename.replace('\0', '') # Remove null characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Prevent reserved names
        reserved = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
        base_name = os.path.splitext(filename)[0].upper()
        if base_name in reserved:
            filename = f"safe_{filename}"
        
        # Clean up code_content if it's wrapped in markdown backticks
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        # Use absolute paths and validate components
        base_dir = os.path.abspath("generated_project")
        filepath = os.path.abspath(os.path.join(base_dir, filename))
        
        # Security: Ensure filepath is within base_dir
        if not filepath.startswith(base_dir):
            return f"Error: Attempted to write outside of generated_project/ directory: {filename}"

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully created {filename} in generated_project/"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool("list_generated_files")
def list_generated_files(dummy: str = ""):
    """
    Useful to see what files have already been created in the generated_project directory.
    """
    try:
        files = []
        for root, _, filenames in os.walk("generated_project"):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), "generated_project")
                files.append(rel_path)
        if not files:
            return "No files generated yet."
        return "Generated files:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

class DevelopmentTools:
    def __init__(self):
        self.write_file_tool = write_file_tool
        self.list_generated_files = list_generated_files