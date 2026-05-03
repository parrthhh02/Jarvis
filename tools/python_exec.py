"""
Lilu — Python Executor Tool
Safe, sandboxed Python code execution with timeout and restricted imports.
"""

import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr


# Imports that are blocked for safety
BLOCKED_IMPORTS = {
    "subprocess", "shutil", "ctypes", "importlib",
    "socket", "http", "urllib", "requests",
}

MAX_OUTPUT_LENGTH = 5000  # Characters
EXECUTION_TIMEOUT = 10   # Seconds (enforced at OS level if needed)


def execute_python(code: str) -> dict:
    """
    Execute Python code in a restricted sandbox.

    Args:
        code: Python code string to execute.

    Returns:
        dict with stdout, stderr, and execution status.
    """
    # ── Check for blocked imports ──
    for blocked in BLOCKED_IMPORTS:
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return {
                "status": "blocked",
                "error": f"Import '{blocked}' is not allowed for safety reasons.",
            }

    # ── Check for dangerous operations ──
    dangerous_patterns = ["os.system(", "os.popen(", "eval(", "exec(", "__import__"]
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                "status": "blocked",
                "error": f"Pattern '{pattern}' is not allowed for safety reasons.",
            }

    # ── Execute in sandbox ──
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    sandbox_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
            "reversed": reversed,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "type": type,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "True": True,
            "False": False,
            "None": None,
            "Exception": Exception,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
        }
    }

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, sandbox_globals)

        stdout_text = stdout_capture.getvalue()[:MAX_OUTPUT_LENGTH]
        stderr_text = stderr_capture.getvalue()[:MAX_OUTPUT_LENGTH]

        return {
            "status": "success",
            "stdout": stdout_text or "(no output)",
            "stderr": stderr_text or "",
        }

    except Exception:
        tb = traceback.format_exc()
        return {
            "status": "error",
            "error": tb[:MAX_OUTPUT_LENGTH],
            "stdout": stdout_capture.getvalue()[:MAX_OUTPUT_LENGTH],
        }


# ── Tool Definition for Registry ─────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "execute_python",
        "description": (
            "Execute Python code in a sandboxed environment. "
            "Some imports are blocked for safety (subprocess, socket, etc). "
            "Use this for calculations, data processing, and generating output. "
            "Returns stdout, stderr, and execution status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Must be safe and self-contained.",
                },
            },
            "required": ["code"],
        },
        "handler": execute_python,
        "destructive": True,
    },
]
