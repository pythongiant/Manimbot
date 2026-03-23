"""
CodeReviewerAgent - Reviews generated Manim code for common issues before rendering.
Runs environment checks (LaTeX availability) and applies safe fixes.
"""
import re
from agents.base import BaseAgent, AgentRole, WorkflowState, WorkflowStatus


class CodeReviewerAgent(BaseAgent):
    """Statically reviews generated code and applies safe fixes before rendering."""

    role = AgentRole.CODE_REVIEWER

    # Patterns that commonly cause rendering failures
    KNOWN_ISSUES = [
        {
            "pattern": r'include_numbers\s*=\s*True',
            "fix": "include_numbers=False",
            "reason": "NumberLine with include_numbers=True causes LaTeX rendering failures",
        },
        {
            "pattern": r'DecimalNumber\(\s*(\d+)\s*\)',
            "fix_fn": lambda m: f'Text("{m.group(1)}")',
            "reason": "DecimalNumber can cause LaTeX issues; Text is safer",
        },
    ]

    def _check_latex_available(self, state: WorkflowState) -> bool:
        """Check if LaTeX is available on this system."""
        # Cache the result in state.environment so we only check once
        if "latex_available" in state.environment:
            return state.environment["latex_available"]

        rc, stdout, stderr = self.run_command(["latex", "--version"])
        available = rc == 0

        if not available:
            # Also check for pdflatex as fallback
            rc2, _, _ = self.run_command(["pdflatex", "--version"])
            available = rc2 == 0

        state.environment["latex_available"] = available
        if not available:
            self.log("LaTeX is NOT available on this system")
        else:
            self.log("LaTeX is available")
        return available

    def _replace_tex_with_text(self, code: str) -> tuple[str, list[str]]:
        """Replace Tex() calls with Text() when LaTeX is not available.
        Preserves MathTex() separately since it needs different handling."""
        fixes = []

        # Replace standalone Tex( with Text( — but NOT MathTex(
        # Negative lookbehind for 'Math' to avoid replacing MathTex
        if re.search(r'(?<!Math)Tex\s*\(', code):
            code = re.sub(r'(?<!Math)Tex\s*\(', 'Text(', code)
            fixes.append("Replaced Tex() with Text() (LaTeX not available)")

        # Replace MathTex( with Text( as well since LaTeX is needed for both
        if re.search(r'MathTex\s*\(', code):
            # For MathTex, strip the LaTeX backslashes for readability
            def mathtex_to_text(m):
                return 'Text('
            code = re.sub(r'MathTex\s*\(', mathtex_to_text, code)
            fixes.append("Replaced MathTex() with Text() (LaTeX not available)")

        return code, fixes

    def _check_has_scene_class(self, code: str) -> bool:
        return bool(re.search(r'class\s+\w+\(Scene\):', code))

    def _check_has_construct(self, code: str) -> bool:
        return bool(re.search(r'def\s+construct\s*\(\s*self\s*\)', code))

    def _check_has_import(self, code: str) -> bool:
        return bool(re.search(r'from\s+manim\s+import', code))

    def _apply_safe_fixes(self, code: str, state: WorkflowState) -> tuple[str, list[str]]:
        """Apply regex-based fixes for known problem patterns."""
        fixed = code
        applied = []

        # Known pattern fixes
        for issue in self.KNOWN_ISSUES:
            if re.search(issue["pattern"], fixed):
                if "fix" in issue:
                    fixed = re.sub(issue["pattern"], issue["fix"], fixed)
                elif "fix_fn" in issue:
                    fixed = re.sub(issue["pattern"], issue["fix_fn"], fixed)
                applied.append(issue["reason"])

        # Environment-aware fixes: replace Tex/MathTex if LaTeX unavailable
        if not self._check_latex_available(state):
            fixed, tex_fixes = self._replace_tex_with_text(fixed)
            applied.extend(tex_fixes)

        return fixed, applied

    def run(self, state: WorkflowState) -> WorkflowState:
        state.status = WorkflowStatus.REVIEWING
        state.current_agent = self.role
        self.log("Reviewing generated code...")

        code = state.generated_code
        if not code:
            state.review_passed = False
            state.review_issues.append("No code to review")
            state.add_error(self.role, "No code was generated")
            return state

        issues = []

        # Structural checks
        if not self._check_has_import(code):
            issues.append("Missing 'from manim import *'")
        if not self._check_has_scene_class(code):
            issues.append("No Scene subclass found")
        if not self._check_has_construct(code):
            issues.append("No construct() method found")

        # Apply safe automatic fixes (now environment-aware)
        fixed_code, fixes_applied = self._apply_safe_fixes(code, state)
        if fixes_applied:
            for fix in fixes_applied:
                self.log(f"Auto-fixed: {fix}")

        state.review_issues = issues
        state.reviewed_code = fixed_code

        if issues:
            state.review_passed = False
            self.log(f"Review found {len(issues)} issue(s): {', '.join(issues)}")
            state.add_message(self.role, f"Review flagged issues: {issues}")
        else:
            state.review_passed = True
            self.log("Review passed")
            state.add_message(self.role, "Code review passed")

        return state
