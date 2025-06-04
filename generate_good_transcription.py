#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from groq import Groq
from pydub import AudioSegment

def trim_audio_to_size(audio_file_path, max_size_mb=24):
    """
    Trim audio file to fit under the size limit by removing from the end
    
    Args:
        audio_file_path (str): Path to the original audio file
        max_size_mb (int): Maximum size in MB (default 24 to stay under 25MB limit)
    
    Returns:
        str: Path to the trimmed audio file
    """
    print(f"Audio file is too large. Trimming to fit under {max_size_mb}MB...")
    
    # Load the audio file
    audio = AudioSegment.from_file(audio_file_path)
    original_duration = len(audio) / 1000  # Duration in seconds
    
    # Get current file size
    current_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    
    # Calculate what percentage to keep
    size_ratio = max_size_mb / current_size_mb
    target_duration = original_duration * size_ratio
    
    # Trim from the end
    trimmed_audio = audio[:int(target_duration * 1000)]  # pydub works in milliseconds
    
    # Create trimmed file path
    base_name = os.path.splitext(audio_file_path)[0]
    extension = os.path.splitext(audio_file_path)[1]
    trimmed_path = f"{base_name}_trimmed{extension}"
    
    # Export trimmed audio
    trimmed_audio.export(trimmed_path, format=extension[1:])  # Remove the dot from extension
    
    trimmed_duration = len(trimmed_audio) / 1000
    removed_duration = original_duration - trimmed_duration
    
    print(f"Original duration: {original_duration:.1f} seconds")
    print(f"Trimmed duration: {trimmed_duration:.1f} seconds")
    print(f"Removed {removed_duration:.1f} seconds from the end")
    print(f"Trimmed file saved as: {trimmed_path}")
    
    return trimmed_path

def transcribe_audio_with_groq(audio_file_path, api_key=None):
    """
    Transcribe audio file using Groq's Whisper API and save to txt file
    
    Args:
        audio_file_path (str): Path to the audio file
        api_key (str): Groq API key (optional, can use environment variable)
    """
    
    # Check file size and trim if necessary
    file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # Size in MB
    if file_size > 25:
        audio_file_path = trim_audio_to_size(audio_file_path)
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output file path
    output_txt_path = os.path.join(output_dir, "original transcription.txt")
    
    # Initialize Groq client
    if api_key:
        client = Groq(api_key=api_key)
    else:
        # Try to get API key from environment variable
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("Error: GROQ_API_KEY environment variable not set.")
            print("Either set the environment variable or pass the API key as an argument.")
            print("Get your free API key from: https://console.groq.com/keys")
            sys.exit(1)
        client = Groq(api_key=api_key)
    
    print(f"Transcribing audio file using Groq API: {audio_file_path}")
    
    try:
        # Open and transcribe the audio file
        with open(audio_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",  # Groq's Whisper model
                response_format="text"
            )
        
        print("Saving transcription to txt file...")
        
        # Write to text file
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            # Add metadata header
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Audio Transcription\n")
            f.write(f"{'='*50}\n")
            f.write(f"File: {os.path.basename(audio_file_path)}\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Model: Groq Whisper Large v3\n")
            f.write(f"{'='*50}\n\n")
            
            # Write the transcription
            f.write(transcription)
        
        print(f"Transcription completed and saved to: {output_txt_path}")
        print(f"Transcription length: {len(transcription)} characters")
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        if "authentication" in str(e).lower():
            print("Please check your Groq API key.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python groq_transcribe.py <audio_file_path> [groq_api_key]")
        print("Example: python groq_transcribe.py meeting.mp3")
        print("Example: python groq_transcribe.py meeting.mp3 your_api_key_here")
        print("\nYou can also set GROQ_API_KEY as an environment variable:")
        print("export GROQ_API_KEY=your_api_key_here")
        print("\nGet your free API key from: https://console.groq.com/keys")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found.")
        sys.exit(1)
    
    # Check file size (after potential trimming)
    file_size = os.path.getsize(audio_file) / (1024 * 1024)  # Size in MB
    if file_size > 25:
        print(f"File size is {file_size:.1f}MB. Trimming to fit under 25MB limit...")
    
    transcribe_audio_with_groq(audio_file, api_key)

if __name__ == "__main__":
    main()