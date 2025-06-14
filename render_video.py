# render_video.py
import bpy
import sys
import os

# Get output path from command line arguments
argv = sys.argv


if "--" in argv:
    out_path = argv[argv.index("--") + 1]

if "-b" in argv:
    temp_path = argv[argv.index("-b") + 1]
else:
    print("No output path provided.")
    sys.exit(1)

dir_path = os.path.dirname(temp_path)
filesave_path = os.path.join(dir_path, out_path.lstrip("/\\"))


scene = bpy.context.scene

# Set output format to FFMPEG video
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'

# Set audio codec and enable audio
scene.render.ffmpeg.audio_codec = 'AAC'
scene.render.ffmpeg.audio_bitrate = 192
scene.render.ffmpeg.audio_channels = 'STEREO'

# Set the scene length based on the sequence editor strips
seq_editor = scene.sequence_editor
if seq_editor and seq_editor.sequences_all:
    last_frame = max(s.frame_final_end for s in seq_editor.sequences_all)
    scene.frame_end = last_frame
    #print(f"Set scene.frame_end to {last_frame}")
else:
    print("No strips found in the sequence editor.")

# Set output file path
scene.render.filepath = filesave_path
print(f"output path= {filesave_path}")

# Render animation (video + audio)
bpy.ops.render.render(animation=True)