import os
from crewai.tools import tool
from logger_config import job_id_var

from memory_store import append_memory, load_memory, summarize_memory


@tool("write_file_tool")
def write_file_tool(data: str):
    """
    Write code to a file under the active project directory.
    Input format: 'relative/path/filename.ext|code_content'
    """
    try:
        if "|" not in data:
            return "Error: Use the format 'filename|content'"

        filename, content = data.split("|", 1)
        filename = filename.strip()

        # Sanitize filename for Windows
        import re

        filename = filename.replace("\0", "")
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        reserved = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        base_name = os.path.splitext(filename)[0].upper()
        if base_name in reserved:
            filename = f"safe_{filename}"

        # Clean up code_content if it's wrapped in markdown backticks
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        try:
            job_id = job_id_var.get()
        except LookupError:
            job_id = "global"
            
        target_dir = os.path.join("jobs", job_id, "generated_project") if job_id != "global" else "generated_project"
        base_dir = os.path.abspath(target_dir)
        filepath = os.path.abspath(os.path.join(base_dir, filename))

        if not filepath.startswith(base_dir):
            return f"Error: Attempted to write outside of {target_dir} directory: {filename}"

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        append_memory(
            "file_events",
            {
                "kind": "file_write",
                "path": filename,
                "summary": f"Agent wrote file {filename}",
            },
        )
        return f"Successfully created {filename} in {target_dir}"
    except Exception as e:
        append_memory(
            "file_events",
            {
                "kind": "file_error",
                "path": filename if "filename" in locals() else "<unknown>",
                "summary": f"Error writing file: {str(e)}",
            },
        )
        return f"Error writing file: {str(e)}"


@tool("list_generated_files")
def list_generated_files(dummy: str = ""):
    """
    List files that exist in the active project directory.
    """
    try:
        try:
            job_id = job_id_var.get()
        except LookupError:
            job_id = "global"
            
        target_dir = os.path.join("jobs", job_id, "generated_project") if job_id != "global" else "generated_project"

        files = []
        if os.path.exists(target_dir):
            for root, _, filenames in os.walk(target_dir):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename), target_dir
                    )
                    files.append(rel_path)
        if not files:
            return "No files generated yet."
        return "Generated files:\n" + "\n".join(sorted(files))
    except Exception as e:
        append_memory(
            "file_events",
            {
                "kind": "file_listing_error",
                "summary": f"Error listing generated files: {str(e)}",
            },
        )
        return f"Error listing files: {str(e)}"


@tool("write_memory")
def write_memory(data: str) -> str:
    """
    Append a short, structured memory entry.
    Input format: 'stream_name|summary text describing the event'
    """
    if "|" not in data:
        return "Error: Use the format 'stream|summary'"
    stream, summary = data.split("|", 1)
    stream = stream.strip() or "project"
    summary = summary.strip()
    append_memory(
        stream,
        {
            "kind": "note",
            "summary": summary,
        },
    )
    return f"Memory appended to stream '{stream}'."


@tool("read_memory")
def read_memory(stream: str = "project") -> str:
    """
    Read a concise textual summary of recent memory for a stream.
    """
    stream = (stream or "project").strip()
    return summarize_memory(stream)


class DevelopmentTools:
    def __init__(self):
        self.write_file_tool = write_file_tool
        self.list_generated_files = list_generated_files
        self.write_memory = write_memory
        self.read_memory = read_memory