import re
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import markdown
from io import StringIO

from config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
    
    async def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a file and return chunked content"""
        try:
            if file_path.suffix.lower() == '.pdf':
                return await self._process_pdf(file_path)
            elif file_path.suffix.lower() == '.md':
                return await self._process_markdown(file_path)
            elif file_path.suffix.lower() == '.txt':
                return await self._process_text(file_path)
            else:
                print(f"Unsupported file type: {file_path.suffix}")
                return []
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []
    
    async def _process_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                
                if not text.strip():
                    return []
                
                return self._chunk_text(text, {
                    "file_type": "pdf",
                    "total_pages": len(reader.pages)
                })
                
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
            return []
    
    async def _process_markdown(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                return []
            
            # Extract title from first heading if available
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            return self._chunk_text(content, {
                "file_type": "markdown",
                "title": title
            })
            
        except Exception as e:
            print(f"Error processing Markdown {file_path}: {e}")
            return []
    
    async def _process_text(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                return []
            
            return self._chunk_text(content, {
                "file_type": "text"
            })
            
        except Exception as e:
            print(f"Error processing text {file_path}: {e}")
            return []
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        # Clean text
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize multiple newlines
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        if not text:
            return []
        
        # Split into sentences for better chunking
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": metadata.copy()
                })
                
                # Start new chunk with overlap
                if len(chunks) > 0 and self.chunk_overlap > 0:
                    # Take last few characters for overlap
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                    current_length = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_length = sentence_length
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_length += sentence_length
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": metadata.copy()
            })
        
        return chunks