"""
TogetherAI API Client for generating Manim code
"""
import json
import os
import re
from typing import Optional
from together import Together


class TogetherAIClient:
    """Client for interacting with TogetherAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the TogetherAI client
        
        Args:
            api_key: TogetherAI API key. If None, will use TOGETHER_API_KEY env var
        """
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY environment variable not set")
        
        self.client = Together(api_key=self.api_key)
        self.model = "moonshotai/Kimi-K2.5"
    
    def generate_code(self, messages: list, max_tokens: int = 8000) -> str:
        """
        Generate code using TogetherAI API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate

        Returns:
            Generated code as string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError("Unexpected response format from TogetherAI API")

        except Exception as e:
            raise RuntimeError(f"API request failed: {str(e)}")

    def _extract_json_text(self, raw: str) -> str:
        """Strip thinking tags and markdown fences, return the JSON string."""
        text = raw.strip()
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        text = re.sub(r'```(?:json)?\s*', '', text).strip()
        # Validate it's actually JSON
        json.loads(text)
        return text

    def generate_json(self, messages: list, max_tokens: int = 2000) -> str:
        """
        Generate a JSON response. Tries response_format first, then falls back
        to a regular call if the model doesn't support structured output.

        Returns:
            Raw response string containing valid JSON.
        """
        # Attempt 1: structured output via response_format
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return self._extract_json_text(content)
        except (json.JSONDecodeError, Exception):
            pass

        # Attempt 2: regular call without response_format (model may ignore it)
        try:
            content = self.generate_code(messages, max_tokens=max_tokens)
            return self._extract_json_text(content)
        except Exception as e:
            raise RuntimeError(f"JSON generation failed: {str(e)}")
    
    def generate_manim_scene(self, user_request: str, context_messages: list = None) -> str:
        """
        Generate a Manim scene based on user request
        
        Args:
            user_request: Description of what the user wants to animate
            context_messages: Optional list of context messages (examples, descriptions)
            
        Returns:
            Generated Python code for a Manim scene
        """
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": """You are an expert Manim animation developer specializing in creating educational videos.

Your task is to generate a complete, executable Manim Python script that explains a concept visually.

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

CODE STRUCTURE:
- Start with: from manim import *
- Include all necessary imports at the top
- Create one Scene class with a construct() method
- Use meaningful variable names
- Add comments explaining key sections
- Use self.play() and self.wait() for timing
- Include self.add() calls for layering objects

ANIMATION BEST PRACTICES:
- Start with a title and context
- Build complexity gradually
- Show intermediate steps, not just final results
- Use colors to highlight important concepts
- Coordinate text and visual animations timing
- End with a summary of what was learned

Generate the complete working code now."""
        })
        
        # Add context messages if provided
        if context_messages:
            messages.extend(context_messages)
        
        # Add user request
        messages.append({
            "role": "user",
            "content": f"""Create a Manim educational animation that explains: {user_request}

Include:
- A clear title at the start
- Step-by-step visual explanation with accompanying text
- Key concepts highlighted with animations and text
- A concluding summary
- All text explanations should be IN the animation using Text objects

Remember: Output ONLY the executable Python code, starting with imports and ending with the Scene class."""
        })
        
        return self.generate_code(messages)
    
    def debug_and_fix_code(self, user_request: str, broken_code: str, error_message: str) -> str:
        """
        Debug and fix broken Manim code by feeding error back to the LLM
        
        Args:
            user_request: Original description of animation
            broken_code: The code that failed to render
            error_message: Error message from the rendering failure
            
        Returns:
            Fixed Python code for a Manim scene
        """
        messages = []
        
        # Add system message for debugging
        messages.append({
            "role": "system",
            "content": """You are an expert Manim animator debugging broken code.

A previous attempt to generate Manim code failed during rendering.
You must analyze the error and generate FIXED code that will work.

CRITICAL REQUIREMENTS:
1. Output ONLY valid Python code - no markdown, no explanations
2. The code must be immediately executable
3. Avoid constructs that cause rendering issues:
   - Do NOT use NumberLine with include_numbers=True
   - Do NOT use DecimalNumber for simple labels
   - Use Text() for simple text labels instead
   - Do NOT use complex Tex() expressions with special characters
4. Simplify the animation logic while keeping the core concept
5. Test your assumptions about available Manim objects
6. Use Text objects instead of complex LaTeX rendering

Remember: The error indicates what went wrong. Fix the specific issue while maintaining the educational intent."""
        })
        
        # Add context with broken code and error
        messages.append({
            "role": "user",
            "content": f"""The previous attempt to generate a Manim scene for '{user_request}' failed.

BROKEN CODE:
```python
{broken_code}
```

ERROR MESSAGE:
```
{error_message[:1000]}
```

Please fix this code. The error tells you what's wrong. Generate corrected code that:
1. Avoids the error that occurred
2. Still demonstrates the concept: {user_request}
3. Uses simpler, more reliable Manim patterns
4. Works immediately without rendering issues

Output ONLY the corrected Python code."""
        })
        
        return self.generate_code(messages)
