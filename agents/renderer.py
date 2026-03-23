"""
RendererAgent - Renders Manim scenes and captures results.
"""
import os
import subprocess
import tempfile
import re
from agents.base import BaseAgent, AgentRole, WorkflowState, WorkflowStatus


class RendererAgent(BaseAgent):
    """Renders Manim code and reports success or failure with diagnostics."""

    role = AgentRole.RENDERER

    def __init__(self, output_dir: str = "./generated_scenes", quality: str = "low", **kwargs):
        super().__init__(**kwargs)
        self.output_dir = output_dir
        self.quality = quality
        self.quality_flags = {"low": "-ql", "medium": "-qm", "high": "-qh"}
        os.makedirs(output_dir, exist_ok=True)

    def _extract_class_name(self, code: str) -> str | None:
        match = re.search(r'class\s+(\w+)\(Scene\):', code)
        return match.group(1) if match else None

    def _classify_error(self, error_msg: str) -> str:
        """Classify a render error to help the debugger choose the right strategy."""
        lower = error_msg.lower()
        if "texmf" in lower or "kpathsea" in lower or "latex" in lower or "dvi" in lower:
            return "latex_environment"
        if "modulenotfounderror" in lower or "importerror" in lower:
            return "missing_import"
        if "nameerror" in lower:
            return "undefined_name"
        if "attributeerror" in lower:
            return "bad_attribute"
        if "typeerror" in lower:
            return "type_error"
        if "syntaxerror" in lower:
            return "syntax_error"
        if "timeout" in lower:
            return "timeout"
        return "unknown"

    def _save_code(self, code: str, scene_name: str) -> str:
        filepath = os.path.join(self.output_dir, f"{scene_name}.py")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        return filepath

    def run(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.RENDERING
        state.current_agent = self.role

        code = state.reviewed_code or state.generated_code
        if not code:
            state.render_success = False
            state.render_error = "No code available to render"
            state.add_error(self.role, state.render_error)
            return state

        scene_name = state.scene_name or self._extract_class_name(code) or "GeneratedScene"
        state.scene_name = scene_name

        # Save code to file
        filepath = self._save_code(code, scene_name)
        state.output_path = filepath
        self.log(f"Code saved to {filepath}")

        # Render
        self.log("Rendering scene...")
        class_name = self._extract_class_name(code)
        if not class_name:
            state.render_success = False
            state.render_error = "Could not find Scene class in code"
            state.add_error(self.role, state.render_error)
            return state

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, dir=self.output_dir
            ) as f:
                f.write(code)
                temp_file = f.name

            cmd = [
                "manim",
                self.quality_flags.get(self.quality, "-ql"),
                temp_file,
                class_name,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                state.render_success = True
                state.render_error = None
                state.add_message(self.role, f"Rendered {class_name} successfully")
                self.log("Render successful")
            else:
                state.render_success = False
                error_output = result.stderr or result.stdout
                state.render_error = error_output

                # Classify the error to help downstream agents
                error_type = self._classify_error(error_output)
                state.environment["last_error_type"] = error_type
                state.add_message(self.role, f"Render failed ({error_type})", error=error_output[:300])
                self.log(f"Render failed — error type: {error_type}")

            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)

        except subprocess.TimeoutExpired:
            state.render_success = False
            state.render_error = "Rendering timed out (5 min limit)"
            state.add_error(self.role, state.render_error)
            self.log("Render timed out")
        except Exception as e:
            state.render_success = False
            state.render_error = str(e)
            state.add_error(self.role, state.render_error)
            self.log(f"Render error: {e}")

        return state
