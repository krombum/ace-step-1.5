import runpod
import base64
import io
import numpy as np
import soundfile as sf
import yaml
import torch
from pathlib import Path
import os

# ACE-Step imports (after pip install -e .)
from ace_step.inference import ACEInference
from ace_step.utils import generate_blueprint_from_lyrics

# Initialize ACE (loads from /workspace/models)
ace = None
def init_ace():
    global ace
    if ace is None:
        model_path = "/workspace/models"
        ace = ACEInference(model_path=model_path)
    return ace

def audio_to_base64(audio_data, sample_rate=44100):
    """Convert numpy audio to base64 WAV"""
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

def handler(job):
    global ace
    
    try:
        input_data = job['input']
        action = input_data.get('action', 'generate')
        
        # Initialize ACE on first request
        ace = init_ace()
        
        if action == 'generate':
            lyrics = input_data['lyrics']
            style = input_data.get('style', 'pop')
            
            # Generate blueprint from lyrics
            blueprint = generate_blueprint_from_lyrics(lyrics, style=style)
            
            # Generate full song
            audio = ace.generate(blueprint)
            
            # Extract stems for karaoke (vocals + instrumental)
            vocal, bgm = ace.separate_stems(audio)
            
            # Generate timestamps (simplified)
            timestamps = {
                'verse_1': [0.0, 15.0],
                'chorus': [15.0, 30.0],
                'verse_2': [30.0, 45.0],
                'chorus_2': [45.0, 60.0]
            }
            
            return {
                "success": True,
                "lyrics": lyrics,
                "timestamps": timestamps,
                "full_audio_b64": audio_to_base64(audio),
                "karaoke_vocal_b64": audio_to_base64(vocal),
                "karaoke_bgm_b64": audio_to_base64(bgm),
                "blueprint": blueprint,
                "duration_seconds": len(audio) / 44100
            }
        
        elif action == 'repaint':
            blueprint = input_data['blueprint']
            section = input_data['section']  # e.g. "chorus"
            new_lyrics = input_data['new_lyrics']
            
            # Regenerate specific section
            edited_audio = ace.repaint(blueprint, section, new_lyrics)
            
            return {
                "success": True,
                "edited_audio_b64": audio_to_base64(edited_audio),
                "section": section
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Start RunPod serverless worker
runpod.serverless.start({"handler": handler})
