import os
import sys
import time
from datetime import datetime
from tqdm import tqdm

from audio_processor import AudioProcessor
from transcriber import Transcriber
from text_merger import TextMerger
from llm_analyzer import LLMAnalyzer
from pdf_generator import PDFGenerator
from config import PATHS, GROQ_CONFIG

class MeetingProcessor:
    def __init__(self):
        print("Initializing Meeting Processor...")
        self.audio_processor = AudioProcessor()
        self.transcriber = Transcriber()
        self.text_merger = TextMerger()
        self.llm_analyzer = LLMAnalyzer()
        self.pdf_generator = PDFGenerator()
        
        os.makedirs(PATHS['output_dir'], exist_ok=True)
        os.makedirs(PATHS['temp_dir'], exist_ok=True)
        
    def process_meeting_audio(self, audio_file_path: str) -> dict:
        start_time = time.time()
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        print(f"\n{'='*60}")
        print(f"PROCESSING MEETING AUDIO: {audio_file_path}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            print("STEP 1: Audio Processing")
            print("-" * 30)
            audio_data = self.audio_processor.load_and_preprocess(audio_file_path)
            chunks = self.audio_processor.create_chunks(audio_data)
            
            if not chunks:
                raise ValueError("No processable audio chunks found (insufficient speech content)")
            
            print(f"✓ Created {len(chunks)} audio chunks for processing\n")
            
            print("STEP 2: Speech-to-Text Transcription")
            print("-" * 30)
            
            transcription_results = []
            
            with tqdm(total=len(chunks), desc="Transcribing chunks") as pbar:
                for i, (chunk_audio, start_time_chunk, end_time_chunk) in enumerate(chunks):
                    temp_filename = f"chunk_{i:03d}_{start_time_chunk:.1f}-{end_time_chunk:.1f}.wav"
                    temp_filepath = self.audio_processor.save_chunk(chunk_audio, temp_filename)
                    
                    result = self.transcriber.transcribe_chunk(temp_filepath)
                    
                    result['chunk_index'] = i
                    result['start_time'] = start_time_chunk
                    result['end_time'] = end_time_chunk
                    transcription_results.append(result)
                    
                    self.transcriber.cleanup_temp_file(temp_filepath)
                    
                    pbar.set_postfix({'chunk': f"{i+1}/{len(chunks)}", 'text_preview': result['text'][:30] + "..."})
                    pbar.update(1)
            
            print(f"✓ Transcribed {len(transcription_results)} chunks\n")
            
            print("STEP 3: Text Merging and Overlap Removal")
            print("-" * 30)
            
            for result in transcription_results:
                if result['success']:
                    chunk_info = {
                        'index': result['chunk_index'],
                        'start_time': result['start_time'],
                        'end_time': result['end_time']
                    }
                    unique_text = self.text_merger.merge_transcription(result['text'], chunk_info)
                    print(f"Chunk {result['chunk_index']:2d}: Added {len(unique_text.split()):3d} new words")
                else:
                    print(f"Chunk {result['chunk_index']:2d}: Skipped due to transcription error")
            
            final_transcript = self.text_merger.get_final_transcript()
            stats = self.text_merger.get_processing_stats()
            
            print(f"✓ Final transcript: {stats['final_word_count']} words, {len(final_transcript)} characters\n")
            
            print("STEP 4: AI Analysis (Meeting Minutes & Action Items)")
            print("-" * 30)
            
            if len(final_transcript.strip()) < 50:
                print("⚠ Warning: Transcript too short for meaningful analysis")
                analysis_results = {
                    'minutes': {'content': 'Transcript too short for analysis', 'success': False},
                    'action_items': {'content': 'Transcript too short for analysis', 'success': False}
                }
            else:
                analysis_results = self.llm_analyzer.analyze_meeting(final_transcript)
            
            print(f"✓ Meeting minutes generated: {analysis_results['minutes']['success']}")
            print(f"✓ Action items extracted: {analysis_results['action_items']['success']}\n")
            
            print("STEP 5: Document Generation")
            print("-" * 30)
            
            analysis_results['transcript'] = final_transcript
            
            generated_files = self.pdf_generator.generate_all_documents(analysis_results)
            
            for doc_type, filepath in generated_files.items():
                print(f"✓ {doc_type.title()}: {filepath}")
            
            end_time = time.time()
            processing_duration = end_time - start_time
            
            print(f"\n{'='*60}")
            print("PROCESSING COMPLETE!")
            print(f"Total time: {processing_duration:.1f} seconds")
            print(f"Audio duration: {len(audio_data)/self.audio_processor.sample_rate:.1f} seconds")
            print(f"Processing ratio: {processing_duration/(len(audio_data)/self.audio_processor.sample_rate):.1f}x")
            print(f"Output files: {len(generated_files)}")
            print(f"{'='*60}\n")
            
            return {
                'success': True,
                'transcript': final_transcript,
                'analysis': analysis_results,
                'generated_files': generated_files,
                'processing_stats': {
                    'audio_duration': len(audio_data)/self.audio_processor.sample_rate,
                    'processing_time': processing_duration,
                    'chunks_processed': len(chunks),
                    'chunks_transcribed': sum(1 for r in transcription_results if r['success']),
                    'final_word_count': stats['final_word_count'],
                    'transcript_length': len(final_transcript)
                },
                'error': None
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transcript': '',
                'analysis': None,
                'generated_files': {},
                'processing_stats': {}
            }
    
    def cleanup_temp_files(self):
        temp_dir = PATHS['temp_dir']
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Warning: Could not remove {filepath}: {e}")

def main():
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = PATHS['test_audio']
    
    if GROQ_CONFIG['api_key'] == 'your-groq-api-key-here':
        print("⚠ WARNING: Please set your GROQ_API_KEY in config.py or as environment variable")
        print("The processor will still work for transcription, but LLM analysis will fail.\n")
    
    processor = MeetingProcessor()
    
    try:
        results = processor.process_meeting_audio(audio_file)
        
        if results['success']:
            print("✅ Meeting processing completed successfully!")
            
            if results['generated_files']:
                print("\n📁 Generated Files:")
                for doc_type, filepath in results['generated_files'].items():
                    print(f"   • {doc_type.title()}: {os.path.basename(filepath)}")
            
            stats = results['processing_stats']
            print(f"\n📊 Processing Statistics:")
            print(f"   • Audio duration: {stats.get('audio_duration', 0):.1f} seconds")
            print(f"   • Processing time: {stats.get('processing_time', 0):.1f} seconds")
            print(f"   • Chunks processed: {stats.get('chunks_processed', 0)}")
            print(f"   • Final word count: {stats.get('final_word_count', 0)}")
            
        else:
            print("❌ Meeting processing failed!")
            print(f"Error: {results['error']}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1
    finally:
        processor.cleanup_temp_files()
    
    return 0

if __name__ == "__main__":
    exit_code = main()