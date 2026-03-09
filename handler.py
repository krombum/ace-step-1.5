import runpod
import base64
import io
from ace_step import ACEInference
import soundfile as sf

ace = ACEInference()

def handler(job):
    input_data = job['input']
    
    if input_data.get('action') == 'generate':
        lyrics = input_data['lyrics']
        style = input_data.get('style', 'pop')
        
        # Generate song
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
            "blueprint": blueprint
        }

runpod.serverless.start({"handler": handler})
