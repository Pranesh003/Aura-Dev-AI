import os
import re
from tools import DevelopmentTools

def test_path_limits():
    tools = DevelopmentTools()
    
    # Test 1: Long path
    long_filename = "a" * 200 + ".py"
    print(f"Testing long filename ({len(long_filename)} chars)...")
    # Call the underlying function directly since it's decorated
    from tools import write_file_tool
    res = write_file_tool._run(f"{long_filename}|print('test')")
    print(f"Result: {res}")
    
    # Test 2: Invalid characters
    bad_filename = "test<>:\"/\\|?*.py"
    print(f"Testing bad characters: {bad_filename}")
    res = write_file_tool._run(f"{bad_filename}|print('test')")
    print(f"Result: {res}")
    
    # Test 3: Reserved names
    reserved_filename = "CON.py"
    print(f"Testing reserved name: {reserved_filename}")
    res = write_file_tool._run(f"{reserved_filename}|print('test')")
    print(f"Result: {res}")

if __name__ == "__main__":
    if not os.path.exists("generated_project"):
        os.makedirs("generated_project")
    test_path_limits()
