import subprocess
import os
from langchain.tools import tool
from langchain_experimental.tools import PythonREPLTool

from .schemas import ReadFileInput, WriteFileInput, ListFilesInput, RunShellInput, PythonReplInput


@tool("read_file", args_schema=ReadFileInput)
def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool("write_file", args_schema=WriteFileInput)
def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path, creating directories as needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool("list_files", args_schema=ListFilesInput)
def list_files(directory: str = ".") -> str:
    """List files and directories at the given path."""
    try:
        entries = os.listdir(directory)
        return "\n".join(sorted(entries)) if entries else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {e}"


@tool("run_shell", args_schema=RunShellInput)
def run_shell(command: str) -> str:
    """Run a shell command and return stdout + stderr. Use with caution."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30 seconds"
    except Exception as e:
        return f"Error running command: {e}"


python_repl = PythonREPLTool(args_schema=PythonReplInput)

ALL_TOOLS = [read_file, write_file, list_files, run_shell, python_repl]
