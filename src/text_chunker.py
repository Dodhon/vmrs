"""
Text Chunker - Splits large documents into processable chunks
"""

from typing import List, Dict
import re


class TextChunker:
    """Chunks text documents while preserving context and structure"""
    
    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target number of tokens per chunk
            overlap: Number of tokens to overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into chunks, preserving sentence boundaries
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries with metadata
        """
        # Split on double newlines (paragraphs) first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Rough token estimate (words * 1.3)
            para_tokens = len(para.split()) * 1.3
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_size + para_tokens > self.chunk_size and current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'index': chunk_index,
                    'text': chunk_text,
                    'token_estimate': current_size,
                    'start_para': chunk_text[:100].replace('\n', ' ')
                })
                
                # Keep overlap for context
                overlap_text = current_chunk[-1] if current_chunk else ''
                current_chunk = [overlap_text, para] if overlap_text else [para]
                current_size = len(overlap_text.split()) * 1.3 + para_tokens
                chunk_index += 1
            else:
                current_chunk.append(para)
                current_size += para_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'index': chunk_index,
                'text': chunk_text,
                'token_estimate': current_size,
                'start_para': chunk_text[:100].replace('\n', ' ')
            })
        
        return chunks
    
    def extract_vmrs_codes(self, text: str) -> List[str]:
        """
        Extract VMRS codes from text (XXX, XXX-XXX, XXX-XXX-XXX format)
        
        Args:
            text: Text to extract codes from
            
        Returns:
            List of unique VMRS codes found
        """
        # Pattern: 3 digits, optionally followed by -3digits, optionally followed by -3digits
        pattern = r'\b(\d{3}(?:-\d{3}(?:-\d{3})?)?)\b'
        codes = re.findall(pattern, text)
        
        # Filter out invalid codes (e.g., years like 2020)
        valid_codes = []
        for code in codes:
            parts = code.split('-')
            # System codes: 001-299 are valid in VMRS
            if len(parts) >= 1:
                system = int(parts[0])
                if 1 <= system <= 299:
                    valid_codes.append(code)
        
        return list(set(valid_codes))



