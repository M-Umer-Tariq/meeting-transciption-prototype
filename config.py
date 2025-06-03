import os
from dotenv import load_dotenv

load_dotenv()

AUDIO_CONFIG = {
    'sample_rate': 16000,        
    'channels': 1,               
    'chunk_duration': 30,        
    'overlap_duration': 8,       
    'min_speech_threshold': 3,   
}

WHISPER_CONFIG = {
    'model_size': 'base',        
    'language': None,            
    'task': 'transcribe',        
}

GROQ_CONFIG = {
    'api_key': os.getenv('GROQ_API_KEY', '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'),
    'model': "llama-3.3-70b-versatile",
    'max_tokens': 2000,
    'temperature': 0.1,          
}

PDF_CONFIG = {
    'font_family': 'Helvetica',
    'title_font_size': 16,
    'body_font_size': 11,
    'margin': 50,                
    'line_spacing': 14,
}

PATHS = {
    'output_dir': 'output',
    'temp_dir': 'temp',
    'test_audio': 'test_data/sample_meeting.mp3',
}