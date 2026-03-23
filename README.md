# ManimAiGen - AI-Powered Manim Animation Generator

Generate beautiful Manim animations using AI. Describe what you want to animate, and the system generates the code and renders it.

## Features

- 🤖 **AI-Powered Generation**: Uses TogetherAI's Kimi-K2-Thinking model to generate Manim code
- 🎨 **Automated Rendering**: Generates and previews animations automatically
- 📚 **Example Context**: Uses a library of examples to improve code generation
- ⚡ **Quick Testing**: Low-quality rendering for fast iteration
- 💾 **Code Persistence**: All generated code is saved for review and reuse

## Demo

https://github.com/user/ManimAiGen/blob/main/GeneratedScene.mp4

## Quick Start (30 Seconds)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
```bash
cp .env.example .env
# Edit .env and add your TogetherAI API key
```

### 3. Run
```bash
python main.py
```

### 4. Describe Your Animation
```
Your request: a blue circle growing and rotating
```

Done! Your animation renders automatically.

### What You Get
- ✅ Generated Manim code (saved in `generated_scenes/`)
- ✅ Rendered video preview (opens automatically)
- ✅ Quick-quality preview for testing

## Detailed Setup Guide

### Project Structure

```
ManimAiGen/
├── main.py                 # Main entry point
├── generator/
│   ├── __init__.py
│   └── ai_client.py       # TogetherAI API client
├── utils/
│   ├── __init__.py
│   ├── prompt_generator.py # Prompt creation utilities
│   └── scene_renderer.py   # Manim rendering engine
├── examples/              # Example animations for context
├── generated_scenes/      # Output directory for generated scenes
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
└── README.md             # This file
```

### Prerequisites

Make sure you have:
- Python 3.10+
- Manim installed and working
- FFmpeg (for video rendering)

### Step-by-Step Setup

#### 1. Clone/Download the Project
```bash
cd ManimAiGen
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure API Key

1. Get a TogetherAI API key from [together.ai](https://www.together.ai/)

2. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API key:
```
TOGETHER_API_KEY=your_actual_api_key_here
```

## Usage

### Basic Usage

```bash
python main.py
```

Then enter your animation description when prompted:

```
Your request: a blue circle that grows larger and rotates 360 degrees while changing to red
```

### What Happens

1. **Prompt Generation**: Your request is enhanced with context from example animations
2. **Code Generation**: AI generates Manim scene code
3. **Saving**: Code is saved to `generated_scenes/`
4. **Rendering**: Scene is rendered at low quality for preview

### Output

Generated scenes are saved in the `generated_scenes/` directory with the scene class name as the filename.

## Examples

### Example 1: Simple Shape Animation
```
Request: Create a green square that morphs into a purple circle with a smooth animation
```

### Example 2: Mathematical Visualization
```
Request: Visualize a sine wave with animated points moving along the curve
```

### Example 3: Multiple Objects
```
Request: Show three bouncing balls of different colors interacting with each other
```

### Additional Example Requests
```
"A red square morphing into a blue circle"
"Three balls bouncing in a triangle pattern"
"A graph showing exponential growth"
"Network diagram with nodes connecting to center"
"Rotating 3D cube with changing colors"
"Plot the sine function with animated points along the curve"
"Show a network diagram with 5 nodes connected to a central node, 
with edges drawing in sequence and nodes appearing in order"
"Create three squares arranged in a row that rotate, scale, and recolor 
in a choreographed sequence"
```

## How It Works

```
User Request
    ↓
Prompt Generator (with examples)
    ↓
TogetherAI API (Kimi-K2-Thinking model)
    ↓
Generated Manim Code
    ↓
Scene Renderer
    ↓
Rendered Video (Preview)
    ↓
Saved Code File
```

## Component Reference

### `generator/ai_client.py`

Handles interaction with TogetherAI API:

- `TogetherAIClient`: Main client for API calls
- Supports custom prompts and message context
- Returns generated Manim code

**Key Methods:**
- `generate_code()`: Generic code generation
- `generate_manim_scene()`: Specialized for Manim scene generation

### `utils/prompt_generator.py`

Creates and manages prompts:

- `create_messages()`: Basic message structure
- `create_messages_from_examples()`: Loads examples as context
- `extract_scenes_from_file()`: Parses multi-scene files
- `create_messages_for_multi_scene_file()`: Handles multi-scene files

### `utils/scene_renderer.py`

Renders Manim scenes:

- `SceneRenderer`: Handles rendering with quality control
- `SceneManager`: Manages the complete workflow
- Saves generated code and renders video previews

**Quality Levels:**
- `low` (default): `-ql` - Fast rendering for testing
- `medium`: `-qm` - Balanced quality
- `high`: `-qh` - High-quality output (slower)

## Tips for Better Results

1. **Be Specific**: Describe exact movements, colors, and timing
2. **Use Examples**: The system learns from examples when generating code
3. **Start Simple**: Test with basic animations first
4. **Review Code**: Check generated code in `generated_scenes/` directory
5. **Iterate**: Refine your requests based on results

## Generating Higher Quality Videos

After testing with low quality, you can render in high quality:

1. Find your generated scene in `generated_scenes/`
2. Render with higher quality:

```bash
manim -qh generated_scenes/your_scene.py YourSceneClassName
```

## Troubleshooting

### API Key Error
```
Error: TOGETHER_API_KEY environment variable not set
```
**Solution:** Make sure your `.env` file exists and contains the API key

### Manim Not Found
```
Error: Manim rendering failed
```
**Solution:** Install Manim and verify it works: `manim --version`

### Rendering Timeout
**Solution:** The scene may be too complex. Simplify or render at a lower quality

### Memory Issues
**Solution:** Reduce quality level or break complex animations into multiple scenes

## Next Steps

- Explore the `examples/` directory for animation patterns
- Modify generated code to fine-tune results
- Create complex animations by combining multiple scenes
- Build animations in the `examples/` directory for training context

## License

MIT

## Support

For issues with:
- **Manim**: [Manim Documentation](https://docs.manim.community/)
- **TogetherAI**: [Together AI Support](https://together.ai/)
- **This Project**: Check the README or create an issue
