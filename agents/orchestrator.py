"""
Orchestrator - Coordinates the agentic workflow pipeline.

Workflow:
  User Request
       |
  [PlannerAgent]  -- creates structured animation plan
       |
  [CodeGeneratorAgent]  -- generates Manim code from plan
       |
  [CodeReviewerAgent]  -- static review & safe auto-fixes
       |
  [RendererAgent]  -- renders scene
       |
  success? ──yes──> Done
       |
      no
       |
  [DebuggerAgent]  -- LLM-powered fix using full context
       |
  [CodeReviewerAgent]  -- re-review the fix
       |
  [RendererAgent]  -- re-render
       |
  (loop up to max_debug_attempts)
"""
import subprocess
from agents.base import WorkflowState, WorkflowStatus
from agents.planner import PlannerAgent
from agents.code_generator import CodeGeneratorAgent
from agents.code_reviewer import CodeReviewerAgent
from agents.renderer import RendererAgent
from agents.debugger import DebuggerAgent


class Orchestrator:
    """Drives the full agentic pipeline from user request to rendered animation."""

    def __init__(
        self,
        ai_client,
        output_dir: str = "./generated_scenes",
        prompts_dir: str = "./prompts",
        quality: str = "low",
        max_debug_attempts: int = 3,
        verbose: bool = True,
    ):
        self.verbose = verbose
        self.prompts_dir = prompts_dir
        self.planner = PlannerAgent(ai_client=ai_client, verbose=verbose)
        self.generator = CodeGeneratorAgent(ai_client=ai_client, verbose=verbose)
        self.reviewer = CodeReviewerAgent(verbose=verbose)
        self.renderer = RendererAgent(
            output_dir=output_dir, quality=quality, verbose=verbose
        )
        self.debugger = DebuggerAgent(ai_client=ai_client, verbose=verbose)
        self.max_debug_attempts = max_debug_attempts

    def _check_environment(self, state: WorkflowState):
        """Run environment checks before the pipeline starts."""
        if self.verbose:
            print("  [env] Checking environment...")

        # Check LaTeX
        try:
            result = subprocess.run(["latex", "--version"], capture_output=True, timeout=10)
            state.environment["latex_available"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            state.environment["latex_available"] = False

        # Check manim
        try:
            result = subprocess.run(["manim", "--version"], capture_output=True, text=True, timeout=10)
            state.environment["manim_available"] = result.returncode == 0
            if result.returncode == 0:
                state.environment["manim_version"] = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            state.environment["manim_available"] = False

        if self.verbose:
            latex = "yes" if state.environment.get("latex_available") else "NO"
            manim = state.environment.get("manim_version", "not found")
            print(f"  [env] LaTeX: {latex} | Manim: {manim}")

    def _banner(self, text: str):
        if self.verbose:
            print(f"\n{'─'*50}")
            print(f"  {text}")
            print(f"{'─'*50}")

    def run(self, user_request: str) -> WorkflowState:
        """Execute the full agentic workflow."""
        state = WorkflowState(
            user_request=user_request,
            max_debug_attempts=self.max_debug_attempts,
            prompts_dir=self.prompts_dir,
        )

        # ── Step 0: Environment Check ──
        self._banner("Step 0 / Environment Check")
        self._check_environment(state)

        # ── Step 1: Plan ──
        self._banner("Step 1 / Plan")
        state = self.planner.run(state)
        if not state.animation_plan:
            state.status = WorkflowStatus.FAILED
            return state

        # ── Step 2: Generate Code ──
        self._banner("Step 2 / Generate Code")
        state = self.generator.run(state)
        if not state.generated_code:
            state.status = WorkflowStatus.FAILED
            return state

        # ── Step 3: Review ──
        self._banner("Step 3 / Review")
        state = self.reviewer.run(state)

        # Even if review flags issues, we still try rendering
        # (the reviewer applies safe fixes to reviewed_code)

        # ── Step 4: Render ──
        self._banner("Step 4 / Render")
        state = self.renderer.run(state)

        if state.render_success:
            state.status = WorkflowStatus.SUCCESS
            return state

        # ── Step 5: Debug Loop ──
        while (
            not state.render_success
            and state.debug_attempts < state.max_debug_attempts
        ):
            self._banner(
                f"Step 5 / Debug (attempt {state.debug_attempts + 1}/{state.max_debug_attempts})"
            )
            state = self.debugger.run(state)

            # Re-review the fix
            state = self.reviewer.run(state)

            # Re-render
            state = self.renderer.run(state)

            if state.render_success:
                state.status = WorkflowStatus.SUCCESS
                return state

        # Exhausted retries
        state.status = WorkflowStatus.FAILED
        return state
