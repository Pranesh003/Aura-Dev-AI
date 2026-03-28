import os
import re

def patch_file(filepath, logger_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add imports
    import_stmt = f"from logger_config import get_logger\nlogger = get_logger('{logger_name}')\n"
    if "from logger_config" not in content:
        content = content.replace("import os", "import os\n" + import_stmt, 1)

    # Patch DEBUG print statements
    content = re.sub(r'print\(f?"DEBUG:\s*(.*?)"\)', r'logger.info(f"\1")', content)
    # Patch tag-based print statements like [ATTEMPT], [QUOTA], etc
    content = re.sub(r'print\(f?"\[([A-Z_]+)\]\s*(.*?)"\)', r'logger.info(f"[\1] \2")', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

base_dir = r"c:\Users\prane\OneDrive\Desktop\visionlink"
patch_file(os.path.join(base_dir, "resilient_engine.py"), "resilient_engine")
patch_file(os.path.join(base_dir, "direct_flow.py"), "direct_flow")
patch_file(os.path.join(base_dir, "crew_flow.py"), "crew_flow")

print("Files successfully patched with logger.")
