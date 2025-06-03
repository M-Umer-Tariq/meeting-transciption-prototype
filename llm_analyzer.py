"""
llm_analyzer.py - Groq LLM integration for meeting analysis

Purpose: Uses Groq API to analyze the complete transcript and generate
meeting minutes and action items with professional formatting.
"""

from typing import Dict, Optional
from config import GROQ_CONFIG
import os

class LLMAnalyzer:
    def __init__(self):
        self.client = None
        self.model = None
        
        # Try to initialize Groq client with error handling
        try:
            # Import Groq here to catch import errors
            from groq import Groq
            
            api_key = GROQ_CONFIG['api_key']
            
            # Check if API key is placeholder
            if api_key == 'your-groq-api-key-here':
                print("⚠ Warning: Groq API key not configured. LLM analysis will be skipped.")
                self.client = None
            else:
                self.client = Groq(api_key=api_key)
                self.model = GROQ_CONFIG['model']
                self.max_tokens = GROQ_CONFIG['max_tokens']
                self.temperature = GROQ_CONFIG['temperature']
                print("✓ Groq client initialized successfully")
                
        except ImportError as e:
            print(f"⚠ Warning: Groq library not available: {e}")
            print("LLM analysis will be skipped. Run: pip install groq")
            self.client = None
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize Groq client: {e}")
            print("LLM analysis will be skipped.")
            self.client = None
    
    def generate_meeting_minutes(self, transcript: str) -> Dict[str, str]:
        """Generate professional meeting minutes from transcript"""
        if self.client is None:
            return {
                'content': "Meeting minutes could not be generated - Groq API not available.\n\nTranscript available separately.",
                'success': False,
                'error': 'Groq API not configured'
            }
        
        prompt = f"""
        Please analyze the following meeting transcript and create professional meeting minutes. 
        Format the output with clear sections and professional language.

        Transcript:
        {transcript}

        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Discussion Points (main topics covered)
        3. Decisions Made (specific decisions and outcomes)
        4. Important Information (key facts, figures, or announcements)

        Format professionally as if for a business document.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            minutes_content = response.choices[0].message.content
            
            return {
                'content': minutes_content,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            print(f"Error generating meeting minutes: {str(e)}")
            return {
                'content': f"Error generating minutes: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def extract_action_items(self, transcript: str) -> Dict[str, str]:
        """Extract action items and tasks from transcript"""
        if self.client is None:
            return {
                'content': "Action items could not be extracted - Groq API not available.\n\nPlease review transcript manually for action items.",
                'success': False,
                'error': 'Groq API not configured'
            }
        
        prompt = f"""
        Analyze the following meeting transcript and extract all action items, tasks, and follow-ups.
        
        Transcript:
        {transcript}

        Please identify:
        1. Specific tasks or action items mentioned
        2. Who is responsible (if mentioned)
        3. Deadlines or timeframes (if mentioned)
        4. Follow-up meetings or check-ins

        Format as a clear list with:
        - Task description
        - Responsible person (if identified)
        - Deadline/timeframe (if mentioned)
        - Priority level (if apparent)

        If no clear action items are found, state "No specific action items identified in this meeting."
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            action_items_content = response.choices[0].message.content
            
            return {
                'content': action_items_content,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            print(f"Error extracting action items: {str(e)}")
            return {
                'content': f"Error extracting action items: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def analyze_meeting(self, transcript: str) -> Dict[str, Dict]:
        """Complete meeting analysis - both minutes and action items"""
        if self.client is None:
            print("Skipping LLM analysis - Groq API not available")
            return {
                'minutes': {
                    'content': 'Meeting minutes not generated - API not configured',
                    'success': False,
                    'error': 'API not available'
                },
                'action_items': {
                    'content': 'Action items not extracted - API not configured', 
                    'success': False,
                    'error': 'API not available'
                },
                'transcript_length': len(transcript),
                'word_count': len(transcript.split())
            }
        
        print("Generating meeting minutes...")
        minutes = self.generate_meeting_minutes(transcript)
        
        print("Extracting action items...")
        action_items = self.extract_action_items(transcript)
        
        return {
            'minutes': minutes,
            'action_items': action_items,
            'transcript_length': len(transcript),
            'word_count': len(transcript.split())
        }