import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import requests
import subprocess
import threading
import platform

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
    # List all video files in the folder
    return [f for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.mov', '.avi'))]

def call_transcript_api(video_path, api_url):
    # Call the transcript API with the video file
    with open(video_path, "rb") as f:
        files = {'file': f}
        resp = requests.post(api_url, files=files)
    resp.raise_for_status()
    return resp.json()

def save_transcript(transcript, out_folder, base_name):
    # Save transcript as JSON in output folder
    out_dir = os.path.join(out_folder, base_name)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(json.dumps(transcript, indent=2, ensure_ascii=False))




def get_default_blender_path():
    system = platform.system()
    if system == "Windows":
        return r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
    elif system == "Darwin":  # MacOS
        return "/Applications/Blender.app/Contents/MacOS/Blender"
    else:  # Linux
        return "/usr/bin/blender"
    
class App:
    def __init__(self, root):
        self.root = root
        self.root.title(CFG["window_title"])
        self.api_url = API_URL
        self.source_folder = SOURCE_FOLDER
        self.output_folder = OUTPUT_FOLDER
        self.status_text = tk.StringVar()
        self.status_text.set("Ready.")
        self.blender_path = get_default_blender_path()
        self.create_widgets()
        self.video_list = []
        self.current_video_index = 0

    def create_widgets(self):
        # Buttons
        tk.Button(self.root, text="Select Blender Executable", command=self.select_blender_executable).pack(fill="x")
        tk.Label(self.root, text="Blender Executable:").pack(fill="x")
        self.blender_path_var = tk.StringVar(value=self.blender_path)
        self.blender_path_entry = tk.Entry(self.root, textvariable=self.blender_path_var, state="readonly")
        tk.Button(self.root, text=CFG["choose_video_folder"], command=self.choose_video_folder).pack(fill="x")
        tk.Button(self.root, text=CFG["choose_transcript"], command=self.choose_transcript).pack(fill="x")
        tk.Button(self.root, text=CFG["select_blender_project"], command=self.select_blender_project).pack(fill="x")
        tk.Button(self.root, text=CFG["update_text_position"], command=self.update_text_position).pack(fill="x")
        tk.Button(self.root, text=CFG["reset_text_position"], command=self.reset_text_position).pack(fill="x")
        tk.Button(self.root, text=CFG["render_video"], command=self.render_video).pack(fill="x")
        # Status/Log area
        self.log = scrolledtext.ScrolledText(self.root, height=10, state="disabled")
        self.log.pack(fill="both", expand=True)
        self.status_label = tk.Label(self.root, textvariable=self.status_text, anchor="w")
        self.status_label.pack(fill="x")

    def log_message(self, msg):
        # Log a message to the GUI log area
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")
        self.status_text.set(msg)

    def choose_video_folder(self):
        folder = filedialog.askdirectory(initialdir=DEFAULT_VIDEO_DIR)
        if folder:
            self.source_folder = folder
            self.video_list = get_video_files(folder)
            if not self.video_list:
                self.log_message("No video files found in selected folder.")
                return
            self.log_message(f"choose_video_folder path={folder}")
            self.current_video_index = 0
            self.process_next_video()

    def process_next_video(self):
        self.log_message("Processing next video")
        # Process videos one by one, waiting for user to click OK after each
        if self.current_video_index >= len(self.video_list):
            self.log_message("All videos processed.")
            return
        video = self.video_list[self.current_video_index]
        base_name = os.path.splitext(os.path.basename(video))[0]
        video_path = os.path.join(self.source_folder, video)
        self.log_message(f"Processing video: {video} base_name={base_name} video_path={video_path}")
        def worker():
            try:
                self.log_message(f"Transcribing {video} ...")
                transcript = call_transcript_api(video_path, self.api_url)
                save_transcript(transcript, self.output_folder, base_name)
                self.import_to_blender(video_path, video_path, transcript, self.output_folder, base_name)
                self.log_message(f"Blender project created for {video}. Click OK to process next video.")
                self.root.after(0, self.show_ok_next)
            except Exception as e:
                self.log_message(f"Failed processing {video}: {e}")
        threading.Thread(target=worker).start()

    def show_ok_next(self):
        # Show OK dialog, then process next video
        if messagebox.askokcancel("Continue", "Click OK to process the next video."):
            self.current_video_index += 1
            self.process_next_video()
        else:
            self.current_video_index = len(self.video_list)
            self.log_message("User input exit processing next video")
            return

    # Save transcript as temp file for Blender script
    def import_to_blender(self, video_path, audio_path, transcript, out_folder, base_name):
        transcript_path = os.path.join(out_folder, base_name, "transcript.txt")
        blender_script = os.path.join(os.path.dirname(__file__), "blender_vse_script.py")
        blender_project = os.path.join(out_folder, base_name, f"{base_name}.blend")
        # Call Blender in background mode
        subprocess.run([
            self.blender_path, "--background", "--python", blender_script,
            "--", video_path, audio_path, transcript_path, blender_project
        ], check=True)

    def choose_transcript(self):
        # Open a file dialog to select a transcript file
        transcript_file = filedialog.askopenfilename(
            title="Open Transcript File",
            filetypes=[("Transcript Files", "*.txt"), ("All Files", "*.*")],
            initialdir=self.output_folder
        )
        if not transcript_file:
            return
        if not os.path.exists(transcript_file):
            self.log_message("No transcript found in selected file.")
            return
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = json.load(f)
        self.edit_transcript(transcript, transcript_file)

    def edit_transcript(self, transcript, transcript_file):
        # Open a window to edit transcript sentences and words
        win = tk.Toplevel(self.root)
        win.title("Edit Transcript")
        sentences = transcript.get("sentences", [])
        words = transcript.get("words", [])
        text = tk.Text(win, width=80, height=20)
        text.pack()
        text.insert("end", "\n".join([s["text"] if isinstance(s, dict) else s for s in sentences]))
        def save_changes():
            new_text = text.get("1.0", "end").strip()
            new_sentences = [{"text": s} for s in new_text.split("\n")]
            transcript["sentences"] = new_sentences
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(transcript, indent=2, ensure_ascii=False))
            win.destroy()
            self.log_message("Transcript updated.")
        tk.Button(win, text="Save", command=save_changes).pack()
        # Word-level editing
        word_frame = tk.Frame(win)
        word_frame.pack()
        word_var = tk.StringVar(value=" ".join([w["text"] if isinstance(w, dict) else w for w in words]))
        word_entry = tk.Entry(word_frame, textvariable=word_var, width=80)
        word_entry.pack(side="left")
        def add_word():
            word = simpledialog.askstring("Add Word", "Enter word to add:")
            if word:
                words.append({"text": word})
                word_var.set(" ".join([w["text"] if isinstance(w, dict) else w for w in words]))
        def remove_word():
            word = simpledialog.askstring("Remove Word", "Enter word to remove:")
            for w in words:
                if (isinstance(w, dict) and w["text"] == word) or w == word:
                    words.remove(w)
                    break
            word_var.set(" ".join([w["text"] if isinstance(w, dict) else w for w in words]))
        #tk.Button(word_frame, text=CFG["add_word"], command=add_word).pack(side="left")
        #tk.Button(word_frame, text=CFG["remove_word"], command=remove_word).pack(side="left")

    def select_blender_executable(self):
        initial_dir = os.path.dirname(self.blender_path)
        filetypes = [("Blender Executable", "blender.exe" if platform.system() == "Windows" else "Blender")]
        path = filedialog.askopenfilename(
            title="Select Blender Executable",
            initialdir=initial_dir,
            filetypes=filetypes
        )
        if path:
            self.blender_path = path
            self.blender_path_var.set(path)
            self.log_message(f"Blender executable set to: {path}")

    # render in blender to output mp4 file
    def render_blender_project(self, blend_file, out_path):
        blender_script = os.path.join(os.path.dirname(__file__), "render_video.py")
        subprocess.run([
            self.blender_path, "-b", blend_file, "--python", blender_script, "--", out_path
        ], check=True)

    def select_blender_project(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if blend_file:
            subprocess.Popen([self.blender_path, blend_file])
            self.log_message(f"Opened Blender project: {blend_file}")
    
    def update_text_position(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if not blend_file:
            return

        # Create a popup window for button selection
        popup = tk.Toplevel(self.root)
        popup.title("Text Position")

        result = {"pos": None}

        def set_position(pos):
            result["pos"] = pos
            popup.destroy()

        tk.Label(popup, text="Set text position:").pack(pady=10)
        tk.Button(popup, text="Top", width=10, command=lambda: set_position(CFG['top'])).pack(pady=5)
        tk.Button(popup, text="Bottom", width=10, command=lambda: set_position(CFG['bottom'])).pack(pady=5)

        # Wait for the popup to close
        self.root.wait_window(popup)

        pos = result["pos"]
        if not pos:
            return

        blender_script = os.path.join(os.path.dirname(__file__), "update_text_position.py")
        subprocess.run([
            self.blender_path, "-b", blend_file, "--python", blender_script, "--", pos
        ])
        self.log_message(f"Updated text position in {blend_file} to {pos}")

    def reset_text_position(self):
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if not blend_file:
            return
        blender_script = os.path.join(os.path.dirname(__file__), "reset_text_position.py")
        subprocess.run([
            self.blender_path, "-b", blend_file, "--python", blender_script
        ])
        self.log_message(f"Reset text position in {blend_file}")

    def render_video(self):
       
        blend_file = filedialog.askopenfilename(filetypes=[("Blender Files", "*.blend")], initialdir=self.output_folder)
        if not blend_file:
            return
        base_name = os.path.splitext(os.path.basename(blend_file))[0]
        out_path = os.path.join(self.output_folder, f"/{base_name}_bps.mp4")
        self.log_message(f"base_name={base_name} Rendering video: {out_path} Will notify, when complete!!! please wait...")
        self.render_blender_project(blend_file, out_path)
        self.log_message(f"Rendered video: {out_path}")



if __name__ == "__main__":
    ensure_dirs()
    root = tk.Tk()
    app = App(root)
    root.mainloop()