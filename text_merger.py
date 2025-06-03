from typing import List
import re

class TextMerger:
    def __init__(self):
        self.accumulated_text = ""
        self.processed_chunks = []
        
    def merge_transcription(self, new_text: str, chunk_info: dict) -> str:
        if not new_text.strip():
            return ""
        
        new_text = self.clean_text(new_text)
        
        if not self.accumulated_text:
            self.accumulated_text = new_text
            unique_text = new_text
        else:
            unique_text = self.remove_overlap(new_text)
            if unique_text:
                self.accumulated_text += " " + unique_text
        
        self.processed_chunks.append({
            'chunk_info': chunk_info,
            'original_text': new_text,
            'unique_text': unique_text,
            'accumulated_length': len(self.accumulated_text)
        })
        
        return unique_text
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text.strip())
        
        text = re.sub(r'\[.*?\]', '', text)  
        text = re.sub(r'\(.*?\)', '', text)  
        
        return text.strip()
    
    def remove_overlap(self, new_text: str) -> str:
        words_accumulated = self.accumulated_text.split()
        words_new = new_text.split()
        
        if len(words_accumulated) == 0 or len(words_new) == 0:
            return new_text
        
        best_overlap_length = self.find_best_overlap(words_accumulated, words_new)
        
        if best_overlap_length > 0:
            unique_words = words_new[best_overlap_length:]
            return " ".join(unique_words)
        else:
            return new_text
    
    def find_best_overlap(self, accumulated_words: List[str], new_words: List[str]) -> int:
        max_overlap = min(len(accumulated_words), len(new_words), 20)  
        best_overlap = 0
        
        for overlap_length in range(max_overlap, 0, -1):
            last_words = accumulated_words[-overlap_length:]
            first_words = new_words[:overlap_length]
            
            if self.sequences_match(last_words, first_words, min_similarity=0.7):
                best_overlap = overlap_length
                break
        
        return best_overlap
    
    def sequences_match(self, seq1: List[str], seq2: List[str], min_similarity: float = 0.8) -> bool:
        if len(seq1) != len(seq2):
            return False
        
        matches = 0
        for w1, w2 in zip(seq1, seq2):
            if self.words_similar(w1, w2):
                matches += 1
        
        similarity = matches / len(seq1)
        return similarity >= min_similarity
    
    def words_similar(self, word1: str, word2: str) -> bool:
        w1 = word1.lower().strip('.,!?:;"')
        w2 = word2.lower().strip('.,!?:;"')
        
        if w1 == w2:
            return True
        
        variations = {
            'and': ['&', 'n'],
            'to': ['2', 'too'],
            'for': ['4', 'fore'],
            'you': ['u'],
            'are': ['r'],
            'see': ['c'],
            'be': ['b'],
        }
        
        for standard, variants in variations.items():
            if (w1 == standard and w2 in variants) or (w2 == standard and w1 in variants):
                return True
        
        if len(w1) <= 3 or len(w2) <= 3:
            return w1 == w2
        
        return self.simple_similarity(w1, w2) > 0.8
    
    def simple_similarity(self, s1: str, s2: str) -> float:
        if not s1 or not s2:
            return 0.0
        
        common = sum(1 for c in s1 if c in s2)
        return common / max(len(s1), len(s2))
    
    def get_final_transcript(self) -> str:
        return self.accumulated_text
    
    def get_processing_stats(self) -> dict:
        return {
            'total_chunks_processed': len(self.processed_chunks),
            'final_transcript_length': len(self.accumulated_text),
            'final_word_count': len(self.accumulated_text.split()),
            'chunks_info': self.processed_chunks
        }