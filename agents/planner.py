"""
PlannerAgent - Analyzes user request and creates a structured animation plan.
"""
import json
import re
from agents.base import BaseAgent, AgentRole, WorkflowState, WorkflowStatus


class PlannerAgent(BaseAgent):
    """Breaks down a user request into a structured animation plan."""

    role = AgentRole.PLANNER

    PLANNING_PROMPT = """You are an animation planning specialist. Given a user's request for a Manim animation,
create a structured plan that a code generator can follow.

Output a JSON object with this exact structure:
{
    "scene_name": "PascalCaseSceneName",
    "title": "Short title shown in the animation",
    "concept": "One-sentence summary of the concept",
    "steps": [
        {
            "description": "What happens in this step",
            "visual_elements": ["list", "of", "manim", "objects"],
            "text_overlay": "Text to show during this step"
        }
    ],
    "colors": {"primary": "BLUE", "secondary": "YELLOW", "accent": "GREEN"},
    "complexity": "low|medium|high",
    "estimated_duration": 10
}

Output ONLY valid JSON, no markdown or explanation."""

    def _parse_json(self, raw: str) -> dict:
        """Parse JSON from LLM output, stripping any residual wrapping."""
        raw = raw.strip()
        # Strip <think>...</think> blocks (thinking models)
        raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
        # Strip markdown fences (shouldn't appear with structured output, but just in case)
        raw = re.sub(r'```(?:json)?\s*', '', raw).strip()
        # Try direct parse first
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        # Find the first { ... } block (greedy match for outermost braces)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise json.JSONDecodeError("No JSON object found in LLM response", raw, 0)

    def run(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.PLANNING
        state.current_agent = self.role
        self.log("Analyzing user request and creating animation plan...")

        messages = [
            {"role": "system", "content": self.PLANNING_PROMPT},
            {"role": "user", "content": state.user_request}
        ]

        # self.save_prompt(state, messages)

        try:
            # Use structured JSON output so the API guarantees valid JSON
            raw = self.ai_client.generate_json(messages, max_tokens=2000)
            plan = self._parse_json(raw)
            state.animation_plan = plan
            state.scene_name = plan.get("scene_name", "GeneratedScene")
            state.add_message(self.role, f"Plan created: {plan.get('title', 'Untitled')}")
            self.log(f"Plan ready: \"{plan.get('title')}\" with {len(plan.get('steps', []))} steps")
        except json.JSONDecodeError:
            self.log("Could not parse plan as JSON, falling back to simple plan")
            state.animation_plan = {
                "scene_name": "GeneratedScene",
                "title": state.user_request[:50],
                "concept": state.user_request,
                "steps": [{"description": state.user_request, "visual_elements": [], "text_overlay": ""}],
                "complexity": "medium",
            }
            state.scene_name = "GeneratedScene"
            state.add_message(self.role, "Used fallback plan (LLM response was not valid JSON)")
        except Exception as e:
            state.add_error(self.role, str(e))
            self.log(f"Planning failed: {e}")
            # Use fallback so the pipeline can continue
            state.animation_plan = {
                "scene_name": "GeneratedScene",
                "title": state.user_request[:50],
                "concept": state.user_request,
                "steps": [{"description": state.user_request, "visual_elements": [], "text_overlay": ""}],
                "complexity": "medium",
            }
            state.scene_name = "GeneratedScene"

        return state
