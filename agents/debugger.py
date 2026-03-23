"""
DebuggerAgent - Fixes broken Manim code using error context and prior attempts.
"""
import json
from agents.base import BaseAgent, AgentRole, WorkflowState, WorkflowStatus
from agents.code_generator import CodeGeneratorAgent


class DebuggerAgent(BaseAgent):
    """Analyzes render errors and generates fixed code using full workflow context."""

    role = AgentRole.DEBUGGER

    SYSTEM_PROMPT = """You are an expert Manim debugger. A Manim animation failed to render.
You have the original plan, the broken code, the error message, the history of prior fix attempts,
and ENVIRONMENT CONSTRAINTS describing what is available on this system.

Your job is to output FIXED, WORKING Python code.

CRITICAL RULES:
1. Output ONLY valid Python code - no markdown, no explanations
2. The code must be immediately executable
3. Respect environment constraints — if LaTeX is not available, use ONLY Text() for all text rendering.
   Do NOT use Tex(), MathTex(), or any LaTeX-dependent objects.
4. Avoid constructs that commonly fail:
   - Do NOT use NumberLine with include_numbers=True
   - Do NOT use DecimalNumber for labels - use Text() instead
5. Simplify where needed but keep the educational intent
6. If a specific Manim API caused the error, use an alternative approach
7. Ensure all referenced variables are defined before use

Generate the complete fixed code now."""

    def run(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.DEBUGGING
        state.current_agent = self.role
        state.debug_attempts += 1
        attempt = state.debug_attempts

        self.log(f"Debug attempt {attempt}/{state.max_debug_attempts}")

        current_code = state.reviewed_code or state.generated_code
        error_msg = state.render_error or "Unknown error"
        plan = state.animation_plan or {}

        # Build environment constraints text
        env_text = ""
        if state.environment:
            env_text = "\n\nENVIRONMENT CONSTRAINTS:\n"
            for key, val in state.environment.items():
                env_text += f"- {key}: {val}\n"
            if not state.environment.get("latex_available", True):
                env_text += (
                    "\nIMPORTANT: LaTeX is NOT installed. You MUST use Text() for ALL text. "
                    "Do NOT use Tex(), MathTex(), or any LaTeX-dependent objects.\n"
                )

        # Build context with full history
        history_text = ""
        if state.debug_history:
            history_text = "\n\nPRIOR FIX ATTEMPTS (do NOT repeat these mistakes):\n"
            for h in state.debug_history:
                history_text += f"- Attempt {h['attempt']}: {h['error'][:200]}\n"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"ORIGINAL REQUEST: {state.user_request}\n\n"
                    f"ANIMATION PLAN:\n{json.dumps(plan, indent=2)}\n\n"
                    f"BROKEN CODE:\n```python\n{current_code}\n```\n\n"
                    f"ERROR MESSAGE:\n```\n{error_msg[:1500]}\n```"
                    f"{env_text}{history_text}\n\n"
                    "Output ONLY the corrected Python code."
                ),
            },
        ]

        # self.save_prompt(state, messages, label=f"attempt{attempt}")

        try:
            raw = self.ai_client.generate_code(messages, max_tokens=8000)
            fixed_code = CodeGeneratorAgent.clean_code_output(raw)

            # Record this attempt
            state.debug_history.append({
                "attempt": attempt,
                "error": error_msg[:300],
                "fixed": True,
            })

            # Feed fixed code back as the reviewed code for re-rendering
            state.reviewed_code = fixed_code
            state.generated_code = fixed_code
            state.add_message(self.role, f"Generated fix (attempt {attempt})")
            self.log("Fix generated, ready for re-render")

        except Exception as e:
            state.debug_history.append({
                "attempt": attempt,
                "error": str(e),
                "fixed": False,
            })
            state.add_error(self.role, str(e))
            self.log(f"Debug failed: {e}")

        return state
