import librosa
import numpy as np
import noisereduce as nr
from scipy.io.wavfile import write
import os
from typing import List, Tuple
from config import AUDIO_CONFIG

class AudioProcessor:
    def __init__(self):
        self.sample_rate = AUDIO_CONFIG['sample_rate']
        self.chunk_duration = AUDIO_CONFIG['chunk_duration']
        self.overlap_duration = AUDIO_CONFIG['overlap_duration']
        self.min_speech_threshold = AUDIO_CONFIG['min_speech_threshold']
        
    def load_and_preprocess(self, audio_path: str) -> np.ndarray:
        print(f"Loading audio file: {audio_path}")
        
        audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
        
        print(f"Audio loaded: {len(audio)/sr:.1f} seconds, {sr}Hz")
        
        print("Applying noise reduction...")
        clean_audio = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.8)
        
        clean_audio = librosa.util.normalize(clean_audio)
        
        return clean_audio
    
    def detect_speech_activity(self, audio_chunk: np.ndarray) -> float:
        rms = librosa.feature.rms(y=audio_chunk, frame_length=2048, hop_length=512)[0]
        
        speech_threshold = np.percentile(rms, 30)
        
        speech_frames = np.sum(rms > speech_threshold)
        total_frames = len(rms)
        
        speech_ratio = speech_frames / total_frames
        chunk_duration = len(audio_chunk) / self.sample_rate
        
        return speech_ratio * chunk_duration
    
    def create_chunks(self, audio: np.ndarray) -> List[Tuple[np.ndarray, float, float]]:
        chunks = []
        total_duration = len(audio) / self.sample_rate
        
        chunk_samples = int(self.chunk_duration * self.sample_rate)
        overlap_samples = int(self.overlap_duration * self.sample_rate)
        step_samples = chunk_samples - overlap_samples
        
        print(f"Creating chunks from {total_duration:.1f}s audio...")
        
        start_idx = 0
        chunk_count = 0
        
        while start_idx < len(audio):
            end_idx = min(start_idx + chunk_samples, len(audio))
            chunk = audio[start_idx:end_idx]
            
            start_time = start_idx / self.sample_rate
            end_time = end_idx / self.sample_rate
            
            speech_duration = self.detect_speech_activity(chunk)
            
            if speech_duration >= self.min_speech_threshold:
                chunks.append((chunk, start_time, end_time))
                chunk_count += 1
                print(f"Chunk {chunk_count}: {start_time:.1f}-{end_time:.1f}s "
                      f"({speech_duration:.1f}s speech) ✓")
            else:
                print(f"Skipping chunk {start_time:.1f}-{end_time:.1f}s "
                      f"({speech_duration:.1f}s speech) - insufficient speech")
            
            start_idx += step_samples
            
            if len(audio) - start_idx < chunk_samples * 0.5:
                break
        
        print(f"Created {len(chunks)} chunks for processing")
        return chunks
    
    def save_chunk(self, chunk: np.ndarray, filename: str) -> str:
        os.makedirs('temp', exist_ok=True)
        
        filepath = f"temp/{filename}"
        
        chunk_int16 = (chunk * 32767).astype(np.int16)
        write(filepath, self.sample_rate, chunk_int16)
        
        return filepath