import runpod
import json
from generate_music import generate_song  # ValyrianTech's actual function

def handler(job):
    """RunPod handler using ValyrianTech's generate_music.py"""
    input_data = job['input']
    
    # Extract lyrics + style from your API request
    lyrics = input_data.get('lyrics', 'Sing a happy song about summer')
    style = input_data.get('style', 'pop')
    
    try:
        # Call ValyrianTech's song generator (handles timestamps + stems)
        result = generate_song(
            lyrics=lyrics,
            style=style,
            timestamps=True,    # Lyrics + timestamps ✓
            stems=True          # Karaoke vocals/instrumental ✓
        )
        
        return {
            "success": True,
            "full_audio": result['audio_path'],
            "vocals": result['vocals_path'],
            "instrumental": result['instrumental_path'],
            "lyrics_timestamps": result['timestamps']
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}

# Standard RunPod serverless start
runpod.serverless.start({"handler": handler})
