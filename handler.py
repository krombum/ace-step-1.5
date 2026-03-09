import os
import runpod
import base64
import io
import torch
from huggingface_hub import login  # HF authentication

# Auto-login with HF token (required for ACE-Step models)
login(token=os.getenv("HF_TOKEN"))

# ACE-Step imports (now authenticated)
from ace_step import ACEInference, generate_blueprint, extract_stems
import soundfile as sf

# Initialize ACE (loads models after HF login)
ace = ACEInference()

def handler(job):
    input_data = job['input']
    
    if input_data.get('action') == 'generate':
        lyrics = input_data['lyrics']
        style = input_data.get('style', 'pop')
        
        # Generate blueprint + full song
        blueprint = generate_blueprint(lyrics, style=style)
        audio, timestamps = ace.generate_full_song(blueprint)
        vocal_track, bgm_track = extract_stems(audio)
        
        # Convert to base64 for direct download
        def audio_to_base64(audio_data):
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 44100, format='WAV')
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')
        
        return {
            "lyrics": lyrics,
            "timestamps": timestamps,
            "full_audio_b64": audio_to_base64(audio),
            "karaoke_vocal_b64": audio_to_base64(vocal_track),
            "karaoke_bgm_b64": audio_to_base64(bgm_track),
            "blueprint": blueprint  # For repaints/edits
        }
    
    elif input_data.get('action') == 'repaint':
        blueprint = input_data['blueprint']
        section = input_data['section']  # e.g. "chorus"
        new_lyrics = input_data['new_lyrics']
        
        edited_audio, new_timestamps = ace.repaint_section(
            blueprint, section, new_lyrics
        )
        
        return {
            "edited_audio_b64": audio_to_base64(edited_audio),
            "new_timestamps": new_timestamps
        }
    
    return {"error": "Use action: 'generate' or 'repaint'"}

# Start RunPod serverless worker
runpod.serverless.start({"handler": handler})
