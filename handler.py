import runpod
import json
import torch
from ace_step import ACEInference
from ace_step.utils import generate_blueprint, extract_stems, save_with_timestamps

ace = ACEInference()  # Loads full ACE-Step 1.5

def handler(job):
    input_data = job['input']
    
    # 1. Generate from lyrics
    if input_data.get('action') == 'generate':
        lyrics = input_data['lyrics']
        style = input_data.get('style', 'pop')
        
        # Generate blueprint + full song
        blueprint = generate_blueprint(lyrics, style=style)
        audio, timestamps = ace.generate_full_song(blueprint)
        
        # Save stems for karaoke
        vocal_track, bgm_track = extract_stems(audio)
        
        return {
            "lyrics": lyrics,
            "timestamps": timestamps,  # Lyrics + timing data
            "full_audio": "s3://your-bucket/song.wav",
            "karaoke_vocal": "s3://your-bucket/vocal.wav",
            "karaoke_bgm": "s3://your-bucket/bgm.wav",
            "blueprint": blueprint  # For repaints
        }
    
    # 2. Repaint/Edit specific section
    elif input_data.get('action') == 'repaint':
        blueprint = input_data['blueprint']
        edit_section = input_data['section']  # e.g. "chorus"
        new_lyrics = input_data['new_lyrics']
        
        # Mask + regenerate section
        edited_audio, new_timestamps = ace.repaint_section(
            blueprint, edit_section, new_lyrics
        )
        
        return {
            "edited_audio": "s3://your-bucket/edited.wav",
            "new_timestamps": new_timestamps
        }
    
    return {"error": "Invalid action"}

# Start RunPod serverless worker
runpod.serverless.start({"handler": handler})
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
