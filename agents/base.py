"""
Base agent class and shared workflow state for the agentic pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json
import os
import subprocess
import time


class AgentRole(Enum):
    PLANNER = "planner"
    CODE_GENERATOR = "code_generator"
    CODE_REVIEWER = "code_reviewer"
    RENDERER = "renderer"
    DEBUGGER = "debugger"


class WorkflowStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    RENDERING = "rendering"
    DEBUGGING = "debugging"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class AgentMessage:
    """A message passed between agents."""
    sender: AgentRole
    content: str
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class WorkflowState:
    """Shared state that flows through the agentic pipeline."""
    # Input
    user_request: str = ""

    # Status tracking
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_agent: Optional[AgentRole] = None

    # Planner output
    animation_plan: Optional[dict] = None

    # Code generator output
    generated_code: Optional[str] = None
    scene_name: Optional[str] = None

    # Reviewer output
    review_passed: bool = False
    review_issues: list = field(default_factory=list)
    reviewed_code: Optional[str] = None

    # Renderer output
    render_success: bool = False
    render_error: Optional[str] = None
    output_path: Optional[str] = None

    # Debugger output
    debug_attempts: int = 0
    max_debug_attempts: int = 3
    debug_history: list = field(default_factory=list)

    # Prompt saving
    prompts_dir: Optional[str] = None

    # Environment constraints discovered at runtime
    environment: dict = field(default_factory=dict)

    # Agent communication log
    messages: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def add_message(self, sender: AgentRole, content: str, **metadata):
        self.messages.append(AgentMessage(
            sender=sender, content=content, metadata=metadata
        ))

    def add_error(self, agent: AgentRole, error: str):
        self.errors.append({"agent": agent.value, "error": error})


class BaseAgent:
    """Base class for all agents in the workflow."""

    role: AgentRole = None

    def __init__(self, ai_client=None, verbose: bool = True):
        self.ai_client = ai_client
        self.verbose = verbose

    def log(self, msg: str):
        if self.verbose:
            print(f"  [{self.role.value}] {msg}")

    def run_command(self, cmd: str | list, timeout: int = 60) -> tuple[int, str, str]:
        """Run a shell command and return (returncode, stdout, stderr)."""
        if isinstance(cmd, str):
            cmd = cmd.split()
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except FileNotFoundError:
            return -1, "", f"Command not found: {cmd[0]}"
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"

    def save_prompt(self, state: WorkflowState, messages: list, label: str = ""):
        """Save prompt messages to the prompts directory."""
        if not state.prompts_dir:
            return
        os.makedirs(state.prompts_dir, exist_ok=True)
        scene = state.scene_name or "unknown"
        suffix = f"_{label}" if label else ""
        filename = f"{scene}_{self.role.value}{suffix}.json"
        filepath = os.path.join(state.prompts_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        self.log(f"Prompt saved to {filepath}")

    def run(self, state: WorkflowState) -> WorkflowState:
        raise NotImplementedError
