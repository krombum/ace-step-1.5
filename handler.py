import runpod
import base64
import os
from pathlib import Path
import soundfile as sf
import io

def audio_to_base64(file_path):
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def handler(job):
    input_data = job['input']
    
    if input_data.get('action') == 'generate':
        lyrics = input_data['lyrics']
        style = input_data.get('style', 'pop')
        
        # Use ACE-Step CLI (matches their production setup)
        import subprocess
        cmd = [
            'python', '/app/ace_step/inference.py',
            '--lyrics', lyrics,
            '--style', style,
            '--output-dir', '/app/outputs',
            '--generate-stems'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Find generated files
        output_dir = Path('/app/outputs')
        audio_files = list(output_dir.glob('*.wav'))
        vocal_files = list(output_dir.glob('*vocal*.wav'))
        bgm_files = list(output_dir.glob('*bgm*.wav'))
        
        return {
            "success": True,
            "lyrics": lyrics,
            "full_audio_b64": audio_to_base64(audio_files[0]) if audio_files else None,
            "karaoke_vocal_b64": audio_to_base64(vocal_files[0]) if vocal_files else None,
            "karaoke_bgm_b64": audio_to_base64(bgm_files[0]) if bgm_files else None
        }

runpod.serverless.start({"handler": handler})
