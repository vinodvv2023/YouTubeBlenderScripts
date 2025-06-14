import os
import json

# Project structure
folders = [
    "videos",
    "output"
]

files = {
    "config.json": {
        "window_title": "Video Transcript & Blender VSE Tool",
        "choose_video_folder": "Choose Video Folder",
        "choose_transcript": "Choose Transcript to View",
        "select_blender_project": "Select Blender Project File",
        "update_text_position": "Update Text Position",
        "reset_text_position": "Reset Text Position",
        "render_video": "Render Video",
        "add_word": "Add Word",
        "remove_word": "Remove Word",
        "top": "Top",
        "bottom": "Bottom",
        "input_text": "Input Text",
        "default_api_url": "http://localhost:8000/transcribe/"
    },
    "requirements.txt": """tkinter
requests
""",
    "README.md": """# Video Transcript & Blender VSE Tool

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
""",
    "HELP.md": """# Help

- **Choose Video Folder:** Select the folder containing your videos. All videos will be processed.
- **Choose Transcript to View:** Pick a transcript to view/edit. You can add/remove words and update the transcript.
- **Select Blender Project File:** Open a Blender project and access the VSE section.
- **Update Text Position:** Set text overlay position (top/bottom/custom Y).
- **Reset Text Position:** Reset all text overlays to default positions.
- **Render Video:** Render the current Blender project. Output is saved as `{filename}_bps.mp4` in the output folder.

All button labels and texts can be changed in `config.json`.
""",
    "sample_usage.md": """# Sample Usage

1. Launch the GUI: `python gui.py`
2. Click "Choose Video Folder" and select your videos directory.
3. The tool will process each video:
   - Call the transcript API
   - Save transcript in `OUTPUT_FOLDER/{video_name}/transcript.txt`
   - Create a Blender project with video/audio imported, text overlays added
4. To view/edit a transcript, click "Choose Transcript to View".
5. To open a Blender project, click "Select Blender Project File".
6. To update text position, use "Update Text Position".
7. To render, click "Render Video".
""",
    "test_gui.py": '''import unittest
import os

class TestFolders(unittest.TestCase):
    def test_source_folder_exists(self):
        self.assertTrue(os.path.exists("videos"))
    def test_output_folder_exists(self):
        self.assertTrue(os.path.exists("output"))

if __name__ == "__main__":
    unittest.main()
''',
    "gui.py": '''import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import requests
import subprocess

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    CFG = json.load(f)

SOURCE_FOLDER = "videos"
OUTPUT_FOLDER = "output"
API_URL = CFG.get("default_api_url", "http://localhost:8000/transcribe/")
DEFAULT_VIDEO_DIR = os.path.abspath(SOURCE_FOLDER)

def ensure_dirs():
    os.makedirs(SOURCE_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_video_files(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.mov', '.avi'))]

def call_transcript_api(video_path, api_url):
    with open(video_path, "rb") as f:
        files = {'file': f}
        resp = requests.post(api_url, files=files)
    resp.raise_for_status()
    return resp.json()

def save_transcript(transcript, out_folder, base_name):
    out_dir = os.path.join(out_folder, base_name)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(json.dumps(transcript, indent=2, ensure_ascii=False))

def import_to_blender(video_path, audio_path, transcript, out_folder, base_name):
    # Save transcript as temp file for Blender script
    transcript_path = os.path.join(out_folder, base_name, "transcript.txt")
    blender_script = os.path.join(os.path.dirname(__file__), "blender_vse_script.py")
    blender_project = os.path.join(out_folder, base_name, f"{base_name}.blend")
    # Call Blender in background mode
    subprocess.run([
        "blender", "--background", "--python", blender_script,
        "--", video_path, audio_path, transcript_path, blender_project
    ], check=True)

def render_blender_project(blend_file, out_path):
    subprocess.run([
        "blender", "-b", blend_file, "-o", out_path, "-a"
    ], check=True)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(CFG["window_title"])
        self.api_url = API_URL
        self.source_folder = SOURCE_FOLDER
        self.output_folder = OUTPUT_FOLDER
        self.setup_gui()

    def setup_gui(self):
        tk.Button(self.root, text=CFG["choose_video_folder"], command=self.choose_video_folder).pack(fill="x")
        tk.Button(self.root, text=CFG["choose_transcript"], command=self.choose_transcript).pack(fill="x")
        tk.Button(self.root, text=CFG["select_blender_project"], command=self.select_blender_project).pack(fill="x")
        tk.Button(self.root, text=CFG["update_text_position"], command=self.update_text_position).pack(fill="x")
        tk.Button(self.root, text=CFG["reset_text_position"], command=self.reset_text_position).pack(fill="x")
        tk.Button(self.root, text=CFG["render_video"], command=self.render_video).pack(fill="x")

    def choose_video_folder(self):
        folder = filedialog.askdirectory(initialdir=DEFAULT_VIDEO_DIR)
        if folder:
            self.source_folder = folder
            videos = get_video_files(folder)
            for video in videos:
                base_name = os.path.splitext(os.path.basename(video))[0]
                video_path = os.path.join(folder, video)
                try:
                    transcript = call_transcript_api(video_path, self.api_url)
                    save_transcript(transcript, self.output_folder, base_name)
                    # Assume audio is in video file
                    import_to_blender(video_path, video_path, transcript, self.output_folder, base_name)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed processing {video}: {e}")

    def choose_transcript(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder)
        if not folder:
            return
        transcript_file = os.path.join(folder, "transcript.txt")
        if not os.path.exists(transcript_file):
            messagebox.showerror("Error", "No transcript found in selected folder.")
            return
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = json.load(f)
        self.edit_transcript(transcript, transcript_file)

    def edit_transcript(self, transcript, transcript_file):
        win = tk.Toplevel(self.root)
        win.title("Edit Transcript")
        sentences = transcript.get("sentences", [])
        words = transcript.get("words", [])
        text = tk.Text(win, width=80, height=20)
        text.pack()
        text.insert("end", "\\n".join(sentences))
        def save_changes():
            new_text = text.get("1.0", "end").strip()
            new_sentences = new_text.split("\\n")
            transcript["sentences"] = new_sentences
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(transcript, indent=2, ensure_ascii=False))
            win.destroy()
        tk.Button(win, text="Save", command=save_changes).pack()
        # Word-level editing
        word_frame = tk.Frame(win)
        word_frame.pack()
        word_var = tk.StringVar(value=" ".join(words))
        word_entry = tk.Entry(word_frame, textvariable=word_var, width=80)
        word_entry.pack(side="left")
        def add_word():
            word = simpledialog.askstring("Add Word", "Enter word to add:")
            if word:
                words.append(word)
                word_var.set(" ".join(words))
        def remove_word():
            word = simpledialog.askstring("Remove Word", "Enter word to remove:")
            if word in words:
                words.remove(word)
                word_var.set(" ".join(words))
        tk.Button(word_frame, text=CFG["add_word"], command=add_word).pack(side="left")
        tk.Button(word_frame, text=CFG["remove_word"], command=remove_word).pack(side="left")

    def select_blender_project(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if blend_file:
            subprocess.Popen(["blender", blend_file])

    def update_text_position(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if not blend_file:
            return
        pos = simpledialog.askstring("Text Position", f"{CFG['top']}/{CFG['bottom']}/Y value:")
        # Call Blender script to update text position
        blender_script = os.path.join(os.path.dirname(__file__), "update_text_position.py")
        subprocess.run([
            "blender", "-b", blend_file, "--python", blender_script, "--", pos
        ])

    def reset_text_position(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if not blend_file:
            return
        blender_script = os.path.join(os.path.dirname(__file__), "reset_text_position.py")
        subprocess.run([
            "blender", "-b", blend_file, "--python", blender_script
        ])

    def render_video(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if not blend_file:
            return
        base_name = os.path.splitext(os.path.basename(blend_file))[0]
        out_path = os.path.join(self.output_folder, f"{base_name}_bps.mp4")
        render_blender_project(blend_file, out_path)

if __name__ == "__main__":
    ensure_dirs()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
''',
    "blender_vse_script.py": '''import bpy
import sys
import os
import json

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # Blender passes all args before -- to itself

video_path, audio_path, transcript_path, blend_out = argv

bpy.ops.sequencer.image_strip_add(directory=os.path.dirname(video_path), files=[{"name": os.path.basename(video_path)}], channel=1, frame_start=1)
bpy.ops.sequencer.sound_strip_add(filepath=audio_path, channel=2, frame_start=1)

with open(transcript_path, "r", encoding="utf-8") as f:
    transcript = json.load(f)

sentences = transcript.get("sentences", [])
words = transcript.get("words", [])

# Add text strips for sentences
for i, sentence in enumerate(sentences):
    bpy.ops.sequencer.effect_strip_add(type='TEXT', channel=3, frame_start=1 + i*30, frame_end=30 + i*30)
    strip = bpy.context.scene.sequence_editor.active_strip
    strip.text = sentence
    strip.use_box = True
    strip.location[1] = 0.9  # Top by default

# Add text strips for words (opacity 0)
for i, word in enumerate(words):
    bpy.ops.sequencer.effect_strip_add(type='TEXT', channel=4, frame_start=1 + i*10, frame_end=10 + i*10)
    strip = bpy.context.scene.sequence_editor.active_strip
    strip.text = word
    strip.use_box = True
    strip.blend_alpha = 0.0

# Set FPS
video = bpy.context.scene.sequence_editor.sequences_all[0]
fps = video.fps if hasattr(video, "fps") else 24
if 29.1 < fps < 29.99:
    bpy.context.scene.render.fps = 30
else:
    bpy.context.scene.render.fps = int(fps)

bpy.ops.wm.save_as_mainfile(filepath=blend_out)
''',
    "update_text_position.py": '''import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]
pos = argv[0].lower()

for strip in bpy.context.scene.sequence_editor.sequences_all:
    if strip.type == 'TEXT':
        if pos == "top":
            strip.location[1] = 0.9
        elif pos == "bottom":
            strip.location[1] = 0.1
        else:
            try:
                y = float(pos)
                strip.location[1] = y
            except:
                pass
bpy.ops.wm.save_mainfile()
''',
    "reset_text_position.py": '''import bpy

for strip in bpy.context.scene.sequence_editor.sequences_all:
    if strip.type == 'TEXT':
        strip.location[1] = 0.9  # Default to top
bpy.ops.wm.save_mainfile()
'''
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Write files
for filename, content in files.items():
    if filename.endswith('.json'):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

print("Project files and folders created. You can now zip the folder if needed.")