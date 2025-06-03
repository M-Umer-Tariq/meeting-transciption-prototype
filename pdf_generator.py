"""
pdf_generator_weasyprint.py - WeasyPrint-based PDF generation

This completely replaces the ReportLab approach with WeasyPrint,
which automatically handles all Markdown formatting beautifully.
"""

import os
from datetime import datetime

# Check if WeasyPrint is available
try:
    import weasyprint
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WeasyPrint not available. Install with: pip install weasyprint")

# Check if Markdown is available
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Markdown not available. Install with: pip install markdown")

class PDFGenerator:
    """
    WeasyPrint-based PDF generator that automatically handles Markdown formatting
    """
    
    def __init__(self):
        self.css_styles = self._get_css_styles()
        
        if not WEASYPRINT_AVAILABLE:
            print("⚠ Warning: WeasyPrint not available. PDF generation will fail.")
            print("Install with: pip install weasyprint")
        
        if not MARKDOWN_AVAILABLE:
            print("⚠ Warning: Markdown not available. Using plain text.")
            print("Install with: pip install markdown")
    
    def _get_css_styles(self) -> str:
        """
        Professional CSS styles for the PDF
        This is where you control the entire look and feel
        """
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Meeting Documentation";
                font-size: 10pt;
                color: #666;
            }
            @bottom-right {
                content: "Page " counter(page);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Arial', 'Helvetica', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        /* Title styling */
        .document-title {
            text-align: center;
            font-size: 24pt;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        .document-date {
            text-align: center;
            font-size: 12pt;
            color: #7f8c8d;
            margin-bottom: 40px;
            font-style: italic;
        }
        
        /* Headers */
        h1 {
            font-size: 18pt;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        
        h2 {
            font-size: 15pt;
            font-weight: bold;
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 12px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 3px;
        }
        
        h3 {
            font-size: 13pt;
            font-weight: bold;
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        h4, h5, h6 {
            font-size: 12pt;
            font-weight: bold;
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 8px;
        }
        
        /* Paragraphs */
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        
        /* Emphasis */
        strong, b {
            font-weight: bold;
            color: #2c3e50;
        }
        
        em, i {
            font-style: italic;
            color: #34495e;
        }
        
        /* Lists */
        ul, ol {
            margin-bottom: 15px;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 6px;
            line-height: 1.5;
        }
        
        ul li {
            list-style-type: disc;
        }
        
        ul ul li {
            list-style-type: circle;
        }
        
        ul ul ul li {
            list-style-type: square;
        }
        
        ol li {
            list-style-type: decimal;
        }
        
        /* Code styling */
        code {
            background-color: #f8f9fa;
            color: #e74c3c;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            line-height: 1.4;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        /* Blockquotes */
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        /* Action items styling */
        .action-item {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
        
        .action-item strong {
            color: #856404;
        }
        
        /* Executive summary styling */
        .executive-summary {
            background-color: #e8f4f8;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        
        /* Responsive design */
        @media print {
            body {
                font-size: 10pt;
            }
            
            .document-title {
                font-size: 20pt;
            }
            
            h1 {
                font-size: 16pt;
            }
            
            h2 {
                font-size: 13pt;
            }
        }
        """
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown text to HTML"""
        if not MARKDOWN_AVAILABLE:
            # Fallback: treat as plain text with basic line break conversion
            return f"<p>{markdown_text.replace(chr(10), '<br>')}</p>"
        
        # Use markdown with extensions for better formatting
        md = markdown.Markdown(
            extensions=[
                'extra',        # Tables, footnotes, etc.
                'codehilite',   # Code syntax highlighting  
                'toc',          # Table of contents
                'nl2br',        # Convert newlines to <br>
                'attr_list',    # Add attributes to elements
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False,  # Use simple highlighting
                }
            }
        )
        
        return md.convert(markdown_text)
    
    def _create_html_document(self, title: str, content_html: str) -> str:
        """Create complete HTML document with title and content"""
        current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                {self.css_styles}
            </style>
        </head>
        <body>
            <div class="document-title">{title}</div>
            <div class="document-date">Generated on {current_date}</div>
            <div class="content">
                {content_html}
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def generate_meeting_minutes(self, minutes_content: str, output_path: str) -> bool:
        """
        Generate meeting minutes PDF from Markdown content
        
        Args:
            minutes_content: Markdown-formatted meeting minutes
            output_path: Path where PDF should be saved
            
        Returns:
            bool: Success status
        """
        if not WEASYPRINT_AVAILABLE:
            print("❌ Cannot generate PDF: WeasyPrint not available")
            return False
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert Markdown to HTML
            content_html = self._markdown_to_html(minutes_content)
            
            # Create complete HTML document
            html_document = self._create_html_document("Meeting Minutes", content_html)
            
            # Generate PDF using WeasyPrint
            HTML(string=html_document).write_pdf(output_path)
            
            print(f"✓ Meeting minutes PDF generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating meeting minutes PDF: {e}")
            return False
    
    def generate_action_items(self, action_items_content: str, output_path: str) -> bool:
        """
        Generate action items PDF from Markdown content
        
        Args:
            action_items_content: Markdown-formatted action items
            output_path: Path where PDF should be saved
            
        Returns:
            bool: Success status
        """
        if not WEASYPRINT_AVAILABLE:
            print("❌ Cannot generate PDF: WeasyPrint not available")
            return False
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert Markdown to HTML
            content_html = self._markdown_to_html(action_items_content)
            
            # Create complete HTML document
            html_document = self._create_html_document("Action Items", content_html)
            
            # Generate PDF using WeasyPrint
            HTML(string=html_document).write_pdf(output_path)
            
            print(f"✓ Action items PDF generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating action items PDF: {e}")
            return False
    
    def generate_transcript(self, transcript_content: str, output_path: str) -> bool:
        """
        Generate transcript PDF (bonus method for completeness)
        
        Args:
            transcript_content: Plain text transcript
            output_path: Path where PDF should be saved
            
        Returns:
            bool: Success status
        """
        if not WEASYPRINT_AVAILABLE:
            print("❌ Cannot generate PDF: WeasyPrint not available")
            return False
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert plain text to HTML with proper formatting
            # Add paragraph breaks for better readability
            formatted_text = transcript_content.replace('\n\n', '</p><p>')
            content_html = f"<p>{formatted_text}</p>"
            
            # Create complete HTML document  
            html_document = self._create_html_document("Meeting Transcript", content_html)
            
            # Generate PDF using WeasyPrint
            HTML(string=html_document).write_pdf(output_path)
            
            print(f"✓ Transcript PDF generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating transcript PDF: {e}")
            return False
    
    def generate_all_documents(self, analysis_results) -> dict:
        """
        Generate all documents (transcript, minutes, action items)
        
        Matches the exact interface expected by main.py
        
        Args:
            analysis_results: Dict containing:
                - 'minutes': {'content': str, 'success': bool}
                - 'action_items': {'content': str, 'success': bool}
                - 'transcript': str (the full transcript)
            
        Returns:
            dict: Mapping of document types to file paths
                {'transcript': 'path/to/file.txt', 'minutes': 'path/to/file.pdf', ...}
        """
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # This will store the results in the format main.py expects
        generated_files = {}
        
        # Ensure output directory exists
        try:
            os.makedirs('output', exist_ok=True)
        except Exception as e:
            print(f"❌ Error creating output directory: {e}")
            return generated_files
        
        # Extract data from analysis_results
        transcript = analysis_results.get('transcript', 'No transcript available.')
        minutes_data = analysis_results.get('minutes', {})
        action_items_data = analysis_results.get('action_items', {})
        
        # Generate transcript file
        transcript_path = f"output/transcript_{timestamp}.txt"
        try:
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(str(transcript))
            generated_files['transcript'] = transcript_path
            print(f"✓ Transcript saved: {transcript_path}")
        except Exception as e:
            print(f"❌ Error saving transcript: {e}")
        
        # Generate meeting minutes PDF
        if minutes_data.get('success', False):
            minutes_path = f"output/meeting_minutes_{timestamp}.pdf"
            minutes_content = minutes_data.get('content', 'No meeting minutes available.')
            
            try:
                if self.generate_meeting_minutes(minutes_content, minutes_path):
                    generated_files['minutes'] = minutes_path
                else:
                    print(f"❌ Failed to generate meeting minutes PDF")
            except Exception as e:
                print(f"❌ Error generating meeting minutes: {e}")
        else:
            print("⚠ Skipping meeting minutes PDF - analysis not successful")
        
        # Generate action items PDF  
        if action_items_data.get('success', False):
            action_items_path = f"output/action_items_{timestamp}.pdf"
            action_items_content = action_items_data.get('content', 'No action items available.')
            
            try:
                if self.generate_action_items(action_items_content, action_items_path):
                    generated_files['action_items'] = action_items_path
                else:
                    print(f"❌ Failed to generate action items PDF")
            except Exception as e:
                print(f"❌ Error generating action items: {e}")
        else:
            print("⚠ Skipping action items PDF - analysis not successful")
        
        return generated_files