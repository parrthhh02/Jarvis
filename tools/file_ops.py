"""
Lilu — File Operations Tool
Read, write, and list files. Write operations require user approval.
"""

import os
from pathlib import Path


def read_file(filepath: str) -> dict:
    """Read the contents of a file."""
    path = Path(filepath)
    if not path.exists():
        return {"error": f"File not found: {filepath}"}
    if not path.is_file():
        return {"error": f"Not a file: {filepath}"}
    try:
        content = path.read_text(encoding="utf-8")
        return {
            "filepath": str(path.resolve()),
            "content": content,
            "size_bytes": path.stat().st_size,
            "lines": len(content.splitlines()),
        }
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}


def write_file(filepath: str, content: str, mode: str = "write") -> dict:
    """
    Write content to a file. Creates parent directories if needed.

    Args:
        filepath: Path to the file.
        content: Content to write.
        mode: 'write' (overwrite) or 'append'.
    """
    path = Path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append":
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "filepath": str(path.resolve()),
            "size_bytes": path.stat().st_size,
            "mode": mode,
        }
    except Exception as e:
        return {"error": f"Failed to write file: {e}"}


def list_directory(dirpath: str = ".", show_hidden: bool = False) -> dict:
    """List contents of a directory."""
    path = Path(dirpath)
    if not path.exists():
        return {"error": f"Directory not found: {dirpath}"}
    if not path.is_dir():
        return {"error": f"Not a directory: {dirpath}"}

    items = []
    try:
        for entry in sorted(path.iterdir()):
            if not show_hidden and entry.name.startswith("."):
                continue
            items.append({
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else None,
            })
        return {
            "directory": str(path.resolve()),
            "item_count": len(items),
            "items": items,
        }
    except PermissionError:
        return {"error": f"Permission denied: {dirpath}"}


# ── Tool Definitions for Registry ────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path. Returns the file content, size, and line count.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read.",
                },
            },
            "required": ["filepath"],
        },
        "handler": read_file,
        "destructive": False,
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file and parent directories if they don't exist. Use mode 'append' to add to existing file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["write", "append"],
                    "description": "'write' to overwrite, 'append' to add to end.",
                    "default": "write",
                },
            },
            "required": ["filepath", "content"],
        },
        "handler": write_file,
        "destructive": True,
    },
    {
        "name": "list_directory",
        "description": "List all files and subdirectories in a given directory path.",
        "parameters": {
            "type": "object",
            "properties": {
                "dirpath": {
                    "type": "string",
                    "description": "Path to the directory to list.",
                    "default": ".",
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Whether to show hidden files (starting with '.').",
                    "default": False,
                },
            },
            "required": [],
        },
        "handler": list_directory,
        "destructive": False,
    },
]
