"""
CodeGeneratorAgent - Generates Manim code from the animation plan.
"""
import json
import re
from pathlib import Path
from agents.base import BaseAgent, AgentRole, WorkflowState, WorkflowStatus


class CodeGeneratorAgent(BaseAgent):
    """Generates executable Manim Python code from a structured plan."""

    role = AgentRole.CODE_GENERATOR

    SYSTEM_PROMPT = """You are an expert Manim animation developer specializing in creating educational videos.

Your task is to generate a complete, executable Manim Python script based on a structured animation plan.

CRITICAL REQUIREMENTS:
1. Output ONLY valid Python code - no markdown, no triple backticks, no explanations outside the code
2. The code must be immediately executable as-is
3. Create ONE Scene class that inherits from Scene
4. Include comprehensive text explanations WITHIN the animation itself using Text objects
5. Use clear, step-by-step animations that build understanding

TEXT IN ANIMATION:
- Add title text explaining what is being demonstrated
- Include step-by-step explanations as objects are animated
- Use the Write animation to introduce text gradually
- Add concluding text that summarizes the concept
- Make text large enough to read clearly (font_size >= 36)
- Make sure the text brings clarity to the concept

CODE STRUCTURE:
- Start with: from manim import *
- Include all necessary imports at the top
- Create one Scene class with a construct() method
- Use meaningful variable names
- Add comments explaining key sections
- Use self.play() and self.wait() for timing

ANIMATION BEST PRACTICES:
- Start with a title and context
- Build complexity gradually
- Show intermediate steps, not just final results
- Use colors to highlight important concepts
- Coordinate text and visual animations timing
- End with a summary of what was learned"""

    @staticmethod
    def clean_code_output(raw: str) -> str:
        """Strip thinking tags, markdown fences, and other wrapping from LLM output."""
        code = raw.strip()
        # Strip <think>...</think> blocks
        code = re.sub(r'<think>.*?</think>', '', code, flags=re.DOTALL).strip()
        # Extract content from markdown code fences (```python ... ``` or ``` ... ```)
        fence_match = re.search(r'```(?:python)?\s*\n(.*?)```', code, re.DOTALL)
        if fence_match:
            code = fence_match.group(1).strip()
        return code

    def _load_examples(self) -> list:
        """Load example animations as few-shot context."""
        examples_dir = Path(__file__).parent.parent / "examples"
        context = []
        if not examples_dir.exists():
            return context
        for f in sorted(examples_dir.iterdir()):
            if f.suffix == ".py":
                try:
                    content = f.read_text(encoding="utf-8")
                    context.append({"role": "user", "content": f"Example animation: {f.name}"})
                    context.append({"role": "assistant", "content": content})
                except Exception:
                    continue
        return context

    def run(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.GENERATING
        state.current_agent = self.role
        self.log("Generating Manim code from plan...")

        plan = state.animation_plan or {}
        plan_text = json.dumps(plan, indent=2) if isinstance(plan, dict) else str(plan)

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add examples as few-shot context
        messages.extend(self._load_examples())

        # Build environment constraints
        env_note = ""
        if not state.environment.get("latex_available", True):
            env_note = (
                "\n\nENVIRONMENT CONSTRAINT: LaTeX is NOT installed on this system. "
                "You MUST use Text() for ALL text rendering. "
                "Do NOT use Tex(), MathTex(), or any LaTeX-dependent objects. "
                "For mathematical expressions, write them as plain text strings in Text()."
            )

        # Build user prompt from the plan
        messages.append({
            "role": "user",
            "content": (
                f"Create a Manim animation based on this plan:\n\n{plan_text}\n\n"
                f"Original user request: {state.user_request}"
                f"{env_note}\n\n"
                "Generate the complete working Python code now. "
                "Output ONLY executable code starting with imports."
            )
        })

        # self.save_prompt(state, messages)

        try:
            code = self.ai_client.generate_code(messages, max_tokens=8000)
            code = self.clean_code_output(code)

            state.generated_code = code
            state.add_message(self.role, "Code generated successfully")
            self.log("Code generation complete")
        except Exception as e:
            state.add_error(self.role, str(e))
            self.log(f"Code generation failed: {e}")

        return state
