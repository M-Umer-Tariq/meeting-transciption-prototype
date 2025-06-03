import whisper
import os
from typing import Dict, Optional
from config import WHISPER_CONFIG

class Transcriber:
    def __init__(self):
        self.model = None
        self.model_size = WHISPER_CONFIG['model_size']
        self.language = WHISPER_CONFIG['language']
        self.task = WHISPER_CONFIG['task']
        
    def load_model(self):
        if self.model is None:
            print(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size)
            print("Whisper model loaded successfully")
    
    def transcribe_chunk(self, audio_file_path: str) -> Dict:
        if self.model is None:
            self.load_model()
        
        try:
            result = self.model.transcribe(
                audio_file_path,
                language=self.language,
                task=self.task,
                verbose=False  
            )
            
            transcription_data = {
                'text': result['text'].strip(),
                'language': result['language'],
                'segments': result.get('segments', []),
                'success': True,
                'error': None
            }
            
            return transcription_data
            
        except Exception as e:
            print(f"Error transcribing chunk: {str(e)}")
            return {
                'text': '',
                'language': 'unknown',
                'segments': [],
                'success': False,
                'error': str(e)
            }
    
    def cleanup_temp_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove temp file {file_path}: {e}")
    
    def get_model_info(self) -> Dict:
        return {
            'model_size': self.model_size,
            'language': self.language,
            'task': self.task,
            'loaded': self.model is not None
        }