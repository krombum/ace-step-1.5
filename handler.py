import runpod
import subprocess
import base64
import os
from pathlib import Path
import json

def handler(job):
    input_data = job['input']
    
    try:
        lyrics = input_data.get('lyrics', 'Test lyrics')
        style = input_data.get('style', 'pop')
        
        # Generate song using ACE-Step CLI
        cmd = [
            'python', '/app/ace_step/inference.py',
            f'--lyrics="{lyrics}"',
            f'--style={style}',
            '--output-dir=/app/outputs',
            '--generate-stems'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Find output files
        output_dir = Path('/app/outputs')
        wav_files = sorted(output_dir.glob('*.wav'), key=os.path.getctime, reverse=True)
        
        audio_b64 = {}
        for wav in wav_files[:3]:  # full, vocal, bgm
            with open(wav, 'rb') as f:
                audio_b64[str(wav.name)] = base64.b64encode(f.read()).decode()
        
        return {
            "success": True,
            "files": audio_b64,
            "lyrics": lyrics,
            "message": "Song generated successfully"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

runpod.serverless.start({"handler": handler})
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
