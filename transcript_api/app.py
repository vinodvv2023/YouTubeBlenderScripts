from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import whisper
import os
import tempfile
from utils import get_video_resolution, map_to_nearest_resolution
import ffmpeg



    
app = FastAPI()
model = whisper.load_model("base")  # You can use "small", "medium", or "large" for better accuracy

@app.post("/transcribe/")
async def transcribe_video(file: UploadFile = File(...)):
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Get video resolution and map to nearest
    width, height = get_video_resolution(tmp_path)
    res_name, res_tuple = map_to_nearest_resolution(width, height)

    # Get FPS using ffmpeg
    # This is optional, but can be useful for debugging or further processing
    probe = ffmpeg.probe(tmp_path)
    video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if video_streams:
        fps = eval(video_streams[0]['r_frame_rate'])
        print(f"FPS: {fps}")
    else:
        print("No video stream found.")    
    # Transcribe using Whisper
    result = model.transcribe(tmp_path, word_timestamps=True)
    os.remove(tmp_path)

    # Structure transcript for Blender
    sentences = []
    words = []
    for segment in result['segments']:
        sentences.append({
            "text": segment['text'],
            "start": segment['start'],
            "end": segment['end']
        })
        for word in segment.get('words', []):
            words.append({
                "text": word['word'],
                "start": word['start'],
                "end": word['end']
            })
    # setting fps to 30 if it is 29.97002997002997
    if(float(fps) >= 29.01 or float(fps) <= 29.99 ):
        fps = 30
    # for debug _response= {"resolution":{"name":"instagram_post","width":1080,"height":1080,"fps":30},"sentences":[{"text":" Yeah, go ahead. So the thing is that I'm on Wi-Fi. Sorry, I'm not on Wi-Fi. I","start":0.0,"end":7.54}],"words":[{"text":" Yeah,","start":0.0,"end":0.46}]}
    return JSONResponse({
        "resolution": {
            "name": res_name,
            "width": res_tuple[0],
            "height": res_tuple[1],
             "fps": fps
        },
        "sentences": sentences,
        "words": words
    })
    # for debug return JSONResponse(_response)

# To run: uvicorn app:app --reload