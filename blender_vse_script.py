import bpy
import sys
import os
import json

# --- VISUAL SETTINGS ---
SAFE_MARGIN = 80
BG_ALPHA = 0.7
FONT_SIZE = 60
LINE_HEIGHT = 120
FADE_DURATION = 10  # frames for fade in/out

# --- CHANNEL MANAGEMENT ---
VIDEO_CHANNEL = 1
AUDIO_CHANNEL = 2
SUBTITLE_BASE_CHANNEL = 4  # Start channel for subtitles
WORD_BASE_CHANNEL = 7  # Start channel for subtitles

argv = sys.argv
argv = argv[argv.index("--") + 1:]

video_path, audio_path, transcript_path, blend_out = argv

# Load transcript
with open(transcript_path, "r", encoding="utf-8") as f:
    transcript = json.load(f)

# Ensure the scene has a sequence editor
scene = bpy.context.scene
scene.render.resolution_x = transcript["resolution"]["width"]
scene.render.resolution_y = transcript["resolution"]["height"]
scene.render.fps = int(transcript["resolution"]["fps"])
scene.render.fps_base = 1.0

# Initialize sequence editor
if not scene.sequence_editor:
    scene.sequence_editor_create()


# --- CLEANUP FUNCTION ---
def clear_existing_sequences():
    """Remove existing video, audio and subtitle strips"""
    if not scene.sequence_editor:
        return
        
    # Collect all sequences to remove
    to_remove = []
    for seq in scene.sequence_editor.sequences_all:
        if seq.type in ['MOVIE', 'SOUND'] or seq.channel >= SUBTITLE_BASE_CHANNEL:
            to_remove.append(seq)
    
    # Remove in reverse order to avoid dependency issues
    for seq in reversed(to_remove):
        try:
            scene.sequence_editor.sequences.remove(seq)
        except:
            pass



# --- VIDEO IMPORT ---
def setup_video_and_audio():
    """Add video and audio strips"""
    try:
        # Video strip
        video_strip = scene.sequence_editor.sequences.new_movie(
            name="Video",
            filepath=video_path,
            channel=VIDEO_CHANNEL,
            frame_start=1
        )
        
        # Audio strip
        audio_strip = scene.sequence_editor.sequences.new_sound(
            name="Audio",
            filepath=video_path,
            channel=AUDIO_CHANNEL,
            frame_start=1
        )
        
        scene.frame_end = int(video_strip.frame_final_duration)
        return True
    except Exception as e:
        print(f"Failed to setup video: {str(e)}")
        return False
# set box active if type is "TEXT"
def setbox(scene):
            #scene = bpy.context.scene
            # Y values: 1.0 is top, 0 is center, -1.0 is bottom
            Y_TOP = 0.85
            Y_BOTTOM = 0

            for seq in scene.sequence_editor.sequences_all:
                if seq.type == 'TEXT':
                    seq.use_box = True

# --- SUBTITLE CREATION ---
def create_subtitle(text, start_frame, end_frame, channel):
    """Create a single subtitle with proper fading"""
    try:
        # Calculate dimensions
        txt_width = scene.render.resolution_x - 2 * SAFE_MARGIN
        y_position = 0.0

        # Text strip
        txt_strip = scene.sequence_editor.sequences.new_effect(
            name=f"TXT_{start_frame}",
            type='TEXT',
            channel=channel+2,
            frame_start=start_frame,
            frame_end=end_frame
        )
        txt_strip.text = text
        txt_strip.font_size = FONT_SIZE
        txt_strip.color = (1, 1, 1, 1)
        
        if hasattr(txt_strip, "text_box"):
            txt_strip.text_box.width = txt_width
            txt_strip.text_box.height = LINE_HEIGHT
            txt_strip.text_box.align_x = 'CENTER'
            txt_strip.text_box.align_y = 'BOTTOM'

        # Transform for background
        trans_bg = scene.sequence_editor.sequences.new_effect(
            name=f"TRANS_{start_frame}",
            type='TRANSFORM',
            channel=channel+1,
            frame_start=start_frame,
            frame_end=end_frame,
            seq1=txt_strip
        )
        
        # Add opactity Zero - This is for word layers, intentionally set the opacity to zero enable, disable to call to this function for word layer opacity aka alpha
        def zero_opacity(strip):
            strip.blend_alpha = 0.0
            strip.keyframe_insert("blend_alpha", frame=start_frame)
            strip.blend_alpha = 0.0
            strip.keyframe_insert("blend_alpha", frame=end_frame)

        # Add fade effects
        def add_fade(strip):
            strip.blend_alpha = 0.0
            strip.keyframe_insert("blend_alpha", frame=start_frame)
            strip.blend_alpha = 1.0
            strip.keyframe_insert("blend_alpha", frame=start_frame + FADE_DURATION)
            strip.blend_alpha = 1.0
            strip.keyframe_insert("blend_alpha", frame=end_frame - FADE_DURATION)
            strip.blend_alpha = 0.0
            strip.keyframe_insert("blend_alpha", frame=end_frame)

        findWordsLen = len(text.split()) #checking whether it is a sentence or word, if sentence add fade effect, for words it is too short to have the effects
        if findWordsLen != 1: 
            add_fade(trans_bg) #enable if needed.
            add_fade(txt_strip)
        else:
            # made the word layers opacity to zero From start frame to end frame
            zero_opacity(txt_strip)
            zero_opacity(trans_bg)
         
        return True
    except Exception as e:
        print(f"Error creating subtitle: {str(e)}")
        return False

# --- MAIN EXECUTION ---
def main():
    # Clear existing sequences
    clear_existing_sequences()
    
    # Setup video and audio
    if not setup_video_and_audio():
        return

    # Process all sentences
    success_count = 0
    for i, sentence in enumerate(transcript["sentences"]):
        start_frame = int(sentence["start"] * scene.render.fps)
        end_frame = int(sentence["end"] * scene.render.fps)
        
        # Use same channel group for all subtitles (they won't overlap in time)
        if create_subtitle(sentence["text"], start_frame, end_frame, SUBTITLE_BASE_CHANNEL):
            success_count += 1
    
    print(f"Successfully added {success_count}/{len(transcript['sentences'])} subtitles")
    
    # creates box for all text layer.
    setbox(scene)

    #enable to create words
    # Process all words
    success_count = 0
    for i, sentence in enumerate(transcript["words"]):
        start_frame = int(sentence["start"] * scene.render.fps)
        end_frame = int(sentence["end"] * scene.render.fps)
        
        # Use same channel group for all subtitles (they won't overlap in time)
        if create_subtitle(sentence["text"], start_frame, end_frame, WORD_BASE_CHANNEL):
            success_count += 1

    print(f"Successfully added {success_count}/{len(transcript['words'])} words")
    
    # Set FPS if not set to imported video fps, the video, audio and text will be out of sync
    fps = transcript.get("resolution", {}).get("fps", 24)
    if 29.1 < float(fps) < 29.99:
        scene.render.fps = 30
    else:
        scene.render.fps = int(fps)

    # Save blender project
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"Project saved to {blend_out}")

if __name__ == "__main__":
    main()
