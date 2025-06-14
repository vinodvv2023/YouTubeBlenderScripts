# Video Transcript & Blender VSE Tool

A cross-platform GUI tool to process videos, transcribe them via API, and automate Blender VSE workflows.

## Features

- Select video folders and process all videos
- View and edit transcripts (sentence/word level)
- Integrate with Blender VSE for text overlay and rendering
- All GUI text is configurable via `config.json`

## Installation

### Prerequisites

- Python 3.11+
- Blender 4.4 (install from [blender.org](https://www.blender.org/download/))
- `pip install -r requirements.txt`

### Platform-specific

#### Windows

1. Install Python 3.11+ and Blender 4.4
2. Add Blender to your PATH
3. Run: `python gui.py`

#### Mac OS

1. Install Python 3.11+ and Blender 4.4
2. Add Blender to your PATH
3. Run: `python3 gui.py`

#### Linux

1. Install Python 3.11+ and Blender 4.4
2. Add Blender to your PATH
3. Run: `python3 gui.py`

## Usage

See `sample_usage.md` for step-by-step instructions.

## Testing

Run `python -m unittest test_gui.py`
