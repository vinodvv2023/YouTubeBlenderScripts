# Video Transcript & Blender VSE Tool - A simple tool for YouTubers to create subtitles and export videos with opensource Blender

A cross-platform GUI tool to process videos from a local folder, transcribe them via API on local machine, and automate Blender VSE workflows.



## Project Structure
Project Structure
```
root/
│
├── gui.py
├── config.json
├── requirements.txt
├── README.md
├── HELP.md
├── test_gui.py
├── sample_usage.md
├── blender_vse_script.py
├── update_text_position.py
├── reset_text_position.py
├── transcript_api/
│   ├── app.py
│   ├── utils.py
│   └── requirements.txt
│   └── README.md
├── videos/
├── output/
```
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

### How this works

This project works with the help of Open AI Whisper, hence you will have to run the API on your local machine. Check the README.md in "transcribe_api" folder

You can now follow rest of the steps below to transcript the video and create subtitles in blender and using blender to render your videos.

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

## RUN Main app

Run `python gui.py`
