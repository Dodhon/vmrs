#!/usr/bin/env python3
"""
Preprocess OCR-generated markdown files to fix common artifacts before extraction.

This script cleans up:
1. Repetitive word patterns (OCR garbage like "second second second...")
2. Excessive whitespace (10+ consecutive spaces)
3. Very long table columns (likely OCR errors)
4. Empty table cells with junk characters
"""

import re
import sys
from pathlib import Path


def remove_repetitive_words(line: str, min_repeats: int = 5) -> str:
    """
    Remove patterns where the same word repeats many times.
    
    Example: "second second second second..." -> ""
    """
    words = line.split()
    cleaned_words = []
    
    i = 0
    while i < len(words):
        word = words[i]
        # Count consecutive occurrences
        count = 1
        while i + count < len(words) and words[i + count] == word:
            count += 1
        
        # If repeated too many times, skip it (it's garbage)
        if count >= min_repeats:
            i += count
        else:
            cleaned_words.extend([word] * count)
            i += count
    
    return ' '.join(cleaned_words)


def normalize_whitespace(line: str, max_consecutive: int = 4) -> str:
    """
    Replace excessive consecutive spaces with a reasonable amount.
    
    Keeps table formatting but removes OCR spacing artifacts.
    """
    # Replace 10+ spaces with max_consecutive spaces
    while '          ' in line:  # 10 spaces
        line = re.sub(r' {10,}', ' ' * max_consecutive, line)
    
    return line


def clean_table_cell(cell: str) -> str:
    """
    Clean individual table cells of junk characters and patterns.
    """
    # Remove common OCR artifacts
    cell = cell.strip()
    
    # Remove excessive dots/bullets
    if re.match(r'^[•\.\-\s]{20,}$', cell):
        return ''
    
    # Clean up spacing
    cell = re.sub(r'\s+', ' ', cell)
    
    return cell


def truncate_long_cells(line: str, max_cell_length: int = 200) -> str:
    """
    Truncate extremely long table cells (likely OCR garbage in last column).
    """
    if not line.strip().startswith('|'):
        return line
    
    # Split by pipe
    parts = line.split('|')
    cleaned_parts = []
    
    for part in parts:
        if len(part) > max_cell_length:
            # Likely garbage - truncate or remove
            cleaned_parts.append(' ')
        else:
            cleaned_parts.append(part)
    
    return '|'.join(cleaned_parts)


def clean_markdown_file(input_path: Path, output_path: Path) -> dict:
    """
    Clean a markdown file and return statistics.
    """
    stats = {
        'total_lines': 0,
        'lines_with_repetition': 0,
        'lines_with_excess_spaces': 0,
        'lines_truncated': 0,
        'bytes_before': 0,
        'bytes_after': 0
    }
    
    print(f"📖 Reading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    stats['total_lines'] = len(lines)
    stats['bytes_before'] = sum(len(line.encode('utf-8')) for line in lines)
    
    print(f"🧹 Cleaning {len(lines)} lines...")
    
    cleaned_lines = []
    for i, line in enumerate(lines, 1):
        original_line = line
        
        # Preserve the original ending (newline or not)
        has_newline = line.endswith('\n')
        line_content = line.rstrip('\n')
        
        # Step 1: Remove repetitive word patterns
        cleaned = remove_repetitive_words(line_content)
        if len(cleaned) < len(line_content) * 0.5:  # Removed more than 50%
            stats['lines_with_repetition'] += 1
        
        # Step 2: Normalize excessive whitespace
        if '          ' in cleaned:  # 10 spaces
            stats['lines_with_excess_spaces'] += 1
        cleaned = normalize_whitespace(cleaned)
        
        # Step 3: Truncate very long table cells
        if len(cleaned) > 500 and '|' in cleaned:
            cleaned = truncate_long_cells(cleaned, max_cell_length=150)
            stats['lines_truncated'] += 1
        
        # Restore newline if it was there
        if has_newline:
            cleaned += '\n'
        
        cleaned_lines.append(cleaned)
        
        # Progress indicator
        if i % 1000 == 0:
            print(f"  Processed {i:,} lines...")
    
    stats['bytes_after'] = sum(len(line.encode('utf-8')) for line in cleaned_lines)
    
    print(f"💾 Writing cleaned file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    return stats


def print_stats(stats: dict):
    """Print cleaning statistics."""
    print("\n" + "="*60)
    print("📊 CLEANING STATISTICS")
    print("="*60)
    print(f"Total lines processed:        {stats['total_lines']:,}")
    print(f"Lines with repetition fixed:  {stats['lines_with_repetition']:,}")
    print(f"Lines with spacing fixed:     {stats['lines_with_excess_spaces']:,}")
    print(f"Lines with cells truncated:   {stats['lines_truncated']:,}")
    print(f"\nFile size before: {stats['bytes_before']:,} bytes ({stats['bytes_before'] / 1024 / 1024:.1f} MB)")
    print(f"File size after:  {stats['bytes_after']:,} bytes ({stats['bytes_after'] / 1024 / 1024:.1f} MB)")
    
    size_reduction = (1 - stats['bytes_after'] / stats['bytes_before']) * 100
    print(f"Size reduction:   {size_reduction:.1f}%")
    print("="*60)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        # Default to the main matching context file
        input_file = Path(__file__).parent.parent / "llm_matching" / "matching_context.md"
    
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    # Create output filename
    output_file = input_file.parent / f"{input_file.stem}_cleaned{input_file.suffix}"
    
    print("🧼 VMRS Markdown OCR Cleaning Tool")
    print("="*60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print("="*60 + "\n")
    
    # Clean the file
    stats = clean_markdown_file(input_file, output_file)
    
    # Print results
    print_stats(stats)
    
    print(f"\n✅ Done! Cleaned file saved to:\n   {output_file}")


if __name__ == "__main__":
    main()

