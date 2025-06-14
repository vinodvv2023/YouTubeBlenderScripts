# Sample Usage

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
