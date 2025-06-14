#import ffmpeg
import subprocess
import json

# Standard resolutions dictionary
RESOLUTIONS = {
    "480p": (854, 480),
    "2k": (2048, 1080),
    "4k": (3840, 2160),
    "8k": (7680, 4320),
    "instagram_story": (1080, 1920),
    "instagram_post": (1080, 1080),
    "youtube": (1920, 1080),
    "facebook": (1280, 720),
    "twitter": (1280, 720)
}

def get_video_resolution(video_path):
    """probe = ffmpeg.probe(video_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    return width, height"""
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    width = info['streams'][0]['width']
    height = info['streams'][0]['height']
    return width, height

def map_to_nearest_resolution(width, height):
    def diff(res):
        return abs(res[0] - width) + abs(res[1] - height)
    nearest = min(RESOLUTIONS.items(), key=lambda x: diff(x[1]))
    return nearest[0], nearest[1]