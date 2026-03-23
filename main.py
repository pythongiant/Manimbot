"""
ManimAiGen - AI-powered Manim animation generation (Agentic Workflow)
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from generator.ai_client import TogetherAIClient
from agents.orchestrator import Orchestrator


def load_environment():
    """Load environment variables from .env file."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print("Warning: .env file not found. Set TOGETHER_API_KEY env var.")


def main():
    load_environment()

    # Initialize AI client
    try:
        ai_client = TogetherAIClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nCreate a .env file with: TOGETHER_API_KEY=your_key_here")
        sys.exit(1)

    # Get user request
    print("\n" + "=" * 60)
    print("  ManimAiGen — Agentic Animation Generator")
    print("=" * 60)
    print("\nDescribe the animation you want to create:")
    print("(Example: 'a blue circle that shrinks and changes to red')\n")

    user_request = input("Your request: ").strip()
    if not user_request:
        print("No request provided. Exiting.")
        sys.exit(0)

    # Run the agentic workflow
    orchestrator = Orchestrator(
        ai_client=ai_client,
        output_dir=str(PROJECT_ROOT / "generated_scenes"),
        prompts_dir=str(PROJECT_ROOT / "prompts"),
        quality="low",
        max_debug_attempts=3,
        verbose=True,
    )

    state = orchestrator.run(user_request)

    # Final report
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Status : {state.status.value}")
    print(f"  Scene  : {state.scene_name}")

    if state.output_path:
        print(f"  Code   : {state.output_path}")

    if state.render_success:
        print(f"  Render : Success")
        if state.video_path:
            print(f"  Video  : {state.video_path}")
    else:
        print(f"  Render : Failed")
        if state.render_error:
            print(f"  Error  : {state.render_error[:200]}")

    if state.debug_attempts > 0:
        print(f"  Debug  : {state.debug_attempts} attempt(s)")

    # Show agent message log
    if state.messages:
        print(f"\n  Agent Log:")
        for msg in state.messages:
            print(f"    [{msg.sender.value}] {msg.content}")

    if state.errors:
        print(f"\n  Errors:")
        for err in state.errors:
            print(f"    [{err['agent']}] {err['error'][:150]}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
