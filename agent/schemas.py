from pydantic import BaseModel, Field, field_validator
from typing import Literal


# --- Tool input schemas ---

class ReadFileInput(BaseModel):
    path: str = Field(..., description="Path to the file to read")


class WriteFileInput(BaseModel):
    path: str = Field(..., description="Path to write the file")
    content: str = Field(..., description="Content to write")


class ListFilesInput(BaseModel):
    directory: str = Field(default=".", description="Directory path to list")


class RunShellInput(BaseModel):
    command: str = Field(..., description="Shell command to execute")

    @field_validator("command")
    @classmethod
    def block_dangerous(cls, v: str) -> str:
        blocked = ["rm -rf /", "format c:", "del /f /s /q c:\\"]
        for pattern in blocked:
            if pattern in v.lower():
                raise ValueError(f"Blocked dangerous command: {pattern}")
        return v


class PythonReplInput(BaseModel):
    query: str = Field(..., description="Python code to execute")


# --- Agent output schemas ---

class CodeOutput(BaseModel):
    """Structured output when the agent produces code."""
    language: Literal["python", "javascript", "bash", "sql", "other"]
    code: str = Field(..., description="The generated code")
    explanation: str = Field(..., description="What the code does")
    filename: str | None = Field(default=None, description="Suggested filename if applicable")


class TaskResult(BaseModel):
    """General structured result from a completed agent task."""
    success: bool
    summary: str = Field(..., description="One-sentence summary of what was done")
    output: str = Field(..., description="Full output or result")
    files_modified: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
