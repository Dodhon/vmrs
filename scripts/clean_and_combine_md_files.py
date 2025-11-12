#!/usr/bin/env python3
"""
Clean and combine all markdown files from md data/ directory.

This script:
1. Cleans each markdown file (removes excessive spaces, OCR artifacts)
2. Combines all files into a single cleaned markdown file
3. Preserves component codes and table structures
"""

import re
import sys
from pathlib import Path
from typing import List, Dict


def remove_repetitive_words(line: str, min_repeats: int = 5) -> str:
    """Remove patterns where the same word repeats many times."""
    words = line.split()
    cleaned_words = []
    
    i = 0
    while i < len(words):
        word = words[i]
        count = 1
        while i + count < len(words) and words[i + count] == word:
            count += 1
        
        if count >= min_repeats:
            i += count
        else:
            cleaned_words.extend([word] * count)
            i += count
    
    return ' '.join(cleaned_words)


def normalize_whitespace(line: str, max_consecutive: int = 4) -> str:
    """Replace excessive consecutive spaces with a reasonable amount."""
    if '|' in line:
        # For table lines, clean up excessive spaces between pipes but preserve structure
        # Split by pipe, clean each cell, then rejoin
        parts = line.split('|')
        cleaned_parts = []
        for part in parts:
            # Replace 5+ consecutive spaces with 2 spaces in table cells
            cleaned = re.sub(r' {5,}', '  ', part)
            cleaned_parts.append(cleaned)
        line = '|'.join(cleaned_parts)
    else:
        # For non-table lines, replace 5+ spaces with max_consecutive
        line = re.sub(r' {5,}', ' ' * max_consecutive, line)
    
    return line


def truncate_long_cells(line: str, max_cell_length: int = 200) -> str:
    """Truncate extremely long table cells (likely OCR garbage)."""
    if not line.strip().startswith('|'):
        return line
    
    parts = line.split('|')
    cleaned_parts = []
    
    for part in parts:
        if len(part.strip()) > max_cell_length:
            # Truncate but keep first part
            cleaned_parts.append(part[:max_cell_length].strip() + '...')
        else:
            cleaned_parts.append(part)
    
    return '|'.join(cleaned_parts)


def clean_markdown_content(content: str) -> str:
    """
    Clean markdown content, preserving structure.
    """
    lines = content.splitlines()
    cleaned_lines = []
    
    for line in lines:
        original_line = line
        
        # Step 1: Remove repetitive word patterns
        cleaned = remove_repetitive_words(line)
        if len(cleaned) < len(line) * 0.5:  # Removed more than 50% = garbage
            cleaned = ''  # Skip this line
        
        # Step 2: Normalize excessive whitespace
        cleaned = normalize_whitespace(cleaned)
        
        # Step 3: Truncate very long table cells
        if len(cleaned) > 500 and '|' in cleaned:
            cleaned = truncate_long_cells(cleaned, max_cell_length=150)
        
        # Skip completely empty lines that were heavily cleaned
        if cleaned.strip():
            cleaned_lines.append(cleaned)
    
    return '\n'.join(cleaned_lines)


def clean_and_combine_md_files(input_dir: Path, output_file: Path) -> Dict:
    """
    Clean all markdown files in input_dir and combine into one file.
    """
    stats = {
        'files_processed': 0,
        'files_with_components': 0,
        'total_bytes_before': 0,
        'total_bytes_after': 0,
        'component_codes_found': set()
    }
    
    # Get all markdown files
    md_files = sorted(input_dir.glob('*.md'))
    
    print(f"📁 Found {len(md_files)} markdown files in {input_dir}")
    print("=" * 70)
    
    combined_content = []
    combined_content.append("# VMRS Complete Handbook - Combined and Cleaned\n\n")
    combined_content.append("This file combines all markdown files from md data/ directory.\n\n")
    combined_content.append("---\n\n")
    
    for i, md_file in enumerate(md_files, 1):
        print(f"📖 Processing [{i}/{len(md_files)}]: {md_file.name}")
        
        try:
            # Read file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            stats['total_bytes_before'] += len(content.encode('utf-8'))
            stats['files_processed'] += 1
            
            # Check for component codes
            component_pattern = r'\b\d{3}-\d{3}-\d{3}\b'
            components = set(re.findall(component_pattern, content))
            if components:
                stats['files_with_components'] += 1
                stats['component_codes_found'].update(components)
                print(f"   ✅ Found {len(components)} component codes")
            
            # Clean the content
            cleaned = clean_markdown_content(content)
            stats['total_bytes_after'] += len(cleaned.encode('utf-8'))
            
            # Add section header and content
            combined_content.append(f"## File: {md_file.name}\n\n")
            combined_content.append(cleaned)
            combined_content.append("\n\n---\n\n")
            
        except Exception as e:
            print(f"   ❌ Error processing {md_file.name}: {e}")
            continue
    
    # Write combined file
    print(f"\n💾 Writing combined file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(combined_content))
    
    stats['total_bytes_after'] = len(''.join(combined_content).encode('utf-8'))
    
    return stats


def print_stats(stats: Dict):
    """Print cleaning statistics."""
    print("\n" + "=" * 70)
    print("📊 CLEANING STATISTICS")
    print("=" * 70)
    print(f"Files processed:              {stats['files_processed']}")
    print(f"Files with component codes:   {stats['files_with_components']}")
    print(f"Unique component codes found: {len(stats['component_codes_found']):,}")
    print(f"\nTotal size before: {stats['total_bytes_before']:,} bytes ({stats['total_bytes_before'] / 1024 / 1024:.1f} MB)")
    print(f"Total size after:  {stats['total_bytes_after']:,} bytes ({stats['total_bytes_after'] / 1024 / 1024:.1f} MB)")
    
    if stats['total_bytes_before'] > 0:
        size_reduction = (1 - stats['total_bytes_after'] / stats['total_bytes_before']) * 100
        print(f"Size reduction:   {size_reduction:.1f}%")
    print("=" * 70)


def main():
    """Main entry point."""
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    input_dir = project_root / "md data"
    output_file = project_root / "llm_matching" / "matching_context_combined_cleaned.md"
    
    if not input_dir.exists():
        print(f"❌ Error: Directory not found: {input_dir}")
        sys.exit(1)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("🧼 VMRS Markdown Cleaner and Combiner")
    print("=" * 70)
    print(f"Input directory:  {input_dir}")
    print(f"Output file:      {output_file}")
    print("=" * 70 + "\n")
    
    # Clean and combine
    stats = clean_and_combine_md_files(input_dir, output_file)
    
    # Print results
    print_stats(stats)
    
    print(f"\n✅ Done! Combined cleaned file saved to:\n   {output_file}")
    print(f"\n📊 Next steps:")
    print(f"   1. Review the combined file")
    print(f"   2. Run extraction on: {output_file.name}")
    print(f"   3. Expected: ~{len(stats['component_codes_found']):,} component codes")


if __name__ == "__main__":
    main()

