import pandas as pd
import re
from collections import Counter, defaultdict

# Load both datasets
vmrs_df = pd.read_csv("csv data/VMRS_COMPLETE_v20_MASTER.csv")
vendor_df = pd.read_csv("vendor data/Master Parts list for Richard 06.25.25 (1).csv")

print("="*80)
print("VMRS TO VENDOR DATA LINKING PATTERNS ANALYSIS")
print("="*80)
print()

# ============================================================================
# PATTERN 1: SYSTEM CODE MATCHING
# ============================================================================
print("PATTERN 1: DIRECT SYSTEM CODE MATCHING")
print("-" * 80)

# Vendor has SYSTEM, COMPONENT, ASSEMBLY columns - may be numeric or alphanumeric
vendor_systems_raw = vendor_df['SYSTEM'].dropna().astype(str)
# Try to zero-pad numeric ones
vendor_systems = []
for sys in vendor_systems_raw.unique():
    try:
        vendor_systems.append(str(int(float(sys))).zfill(3))
    except (ValueError, TypeError):
        vendor_systems.append(sys)

vendor_systems = list(set(vendor_systems))
vmrs_systems = vmrs_df['system'].dropna().unique()

common_systems = set(vendor_systems) & set(vmrs_systems)

print(f"Vendor unique systems: {len(vendor_systems)}")
print(f"VMRS unique systems: {len(vmrs_systems)}")
print(f"Common systems: {len(common_systems)}")
if len(vendor_systems) > 0:
    print(f"Overlap percentage: {len(common_systems)/len(vendor_systems)*100:.1f}%")
print()
print(f"Sample vendor systems: {sorted([s for s in vendor_systems if s.isdigit()])[:20]}")
print(f"Common systems (first 20): {sorted(list(common_systems))[:20]}")
print()

# ============================================================================
# PATTERN 2: SYSTEM-COMPONENT-ASSEMBLY CODE CONSTRUCTION
# ============================================================================
print("\nPATTERN 2: VENDOR CODE CONSTRUCTION TO VMRS")
print("-" * 80)

# Vendor has CLASS, SYSTEM, COMPONENT, ASSEMBLY columns
# Let's see if we can construct VMRS codes from these

def safe_format_code(val, width=3):
    """Safely format a value to a zero-padded string of specified width"""
    try:
        return str(int(float(val))).zfill(width)
    except (ValueError, TypeError):
        return None

# Filter to records with numeric SYSTEM and COMPONENT
vendor_temp = vendor_df[
    vendor_df['SYSTEM'].notna() & 
    vendor_df['COMPONENT'].notna()
].copy()

vendor_temp['sys_fmt'] = vendor_temp['SYSTEM'].apply(safe_format_code)
vendor_temp['comp_fmt'] = vendor_temp['COMPONENT'].apply(safe_format_code)
vendor_temp['asm_fmt'] = vendor_temp['ASSEMBLY'].fillna(0).apply(safe_format_code)

vendor_with_codes = vendor_temp[
    vendor_temp['sys_fmt'].notna() &
    vendor_temp['comp_fmt'].notna() &
    vendor_temp['asm_fmt'].notna()
].copy()

# Construct potential VMRS codes from vendor data
vendor_with_codes['constructed_code'] = (
    vendor_with_codes['sys_fmt'] + '-' +
    vendor_with_codes['comp_fmt'] + '-' +
    vendor_with_codes['asm_fmt']
)

# Check if these constructed codes exist in VMRS
vmrs_9digit = set(vmrs_df['code_9d'].dropna())
vmrs_6digit = set(vmrs_df['code_6d'].dropna())

vendor_9digit_matches = vendor_with_codes['constructed_code'].isin(vmrs_9digit).sum()
total_vendor_constructed = len(vendor_with_codes)

print(f"Vendor records with complete numeric codes: {total_vendor_constructed}")
print(f"Matching 9-digit VMRS codes: {vendor_9digit_matches}")
print(f"Match rate: {vendor_9digit_matches/total_vendor_constructed*100:.1f}%")
print()

# Show some examples
matched_examples = vendor_with_codes[
    vendor_with_codes['constructed_code'].isin(vmrs_9digit)
].head(10)

if len(matched_examples) > 0:
    print("Example matches:")
    for idx, row in matched_examples.iterrows():
        code = row['constructed_code']
        desc = str(row['DESCRIPTION']) if pd.notna(row['DESCRIPTION']) else 'N/A'
        vmrs_match = vmrs_df[vmrs_df['code_9d'] == code]
        if len(vmrs_match) > 0:
            vmrs_desc = str(vmrs_match['description'].iloc[0]) if pd.notna(vmrs_match['description'].iloc[0]) else 'N/A'
            print(f"  {code}: Vendor='{desc[:40]}' | VMRS='{vmrs_desc[:40]}'")
print()

# ============================================================================
# PATTERN 3: DESCRIPTION TEXT MATCHING PATTERNS
# ============================================================================
print("\nPATTERN 3: DESCRIPTION KEYWORD OVERLAP")
print("-" * 80)

# Extract common keywords from both datasets
def extract_keywords(text):
    if pd.isna(text):
        return []
    # Remove special chars, split, lowercase
    words = re.findall(r'\b[a-zA-Z]{3,}\b', str(text).lower())
    # Filter out common words
    stopwords = {'and', 'the', 'for', 'with', 'from', 'assembly', 'component'}
    return [w for w in words if w not in stopwords]

vmrs_keywords = Counter()
for desc in vmrs_df['description'].dropna():
    vmrs_keywords.update(extract_keywords(desc))

vendor_keywords = Counter()
for desc in vendor_df['DESCRIPTION'].dropna():
    vendor_keywords.update(extract_keywords(desc))

# Find common keywords
common_keywords = set(vmrs_keywords.keys()) & set(vendor_keywords.keys())

print(f"Total VMRS unique keywords: {len(vmrs_keywords)}")
print(f"Total Vendor unique keywords: {len(vendor_keywords)}")
print(f"Common keywords: {len(common_keywords)}")
print()

# Top shared keywords
shared_keyword_scores = {
    k: (vmrs_keywords[k], vendor_keywords[k]) 
    for k in common_keywords
}
top_shared = sorted(
    shared_keyword_scores.items(), 
    key=lambda x: min(x[1][0], x[1][1]), 
    reverse=True
)[:30]

print("Top 30 shared keywords (likely component types):")
for keyword, (vmrs_count, vendor_count) in top_shared:
    print(f"  {keyword:20} | VMRS: {vmrs_count:4} | Vendor: {vendor_count:4}")
print()

# ============================================================================
# PATTERN 4: CLASS MAPPING
# ============================================================================
print("\nPATTERN 4: CLASS/CATEGORY ALIGNMENT")
print("-" * 80)

vendor_classes = vendor_df['CLASS'].dropna().unique()
print(f"Vendor classes: {len(vendor_classes)}")
print(f"Examples: {list(vendor_classes)[:15]}")
print()

# Group VMRS systems by major categories (manual categorization hint)
print("VMRS systems appear to be hierarchical codes (001-999)")
print("These likely map to broad equipment categories")
print()

# ============================================================================
# PATTERN 5: HIERARCHICAL RELATIONSHIP STRUCTURE
# ============================================================================
print("\nPATTERN 5: HIERARCHICAL STRUCTURE COMPARISON")
print("-" * 80)

print("VMRS Structure:")
print("  System (XXX) -> Subcode/Assembly (XXX) -> Component (XXX)")
print("  Example: 001-002-064")
print()

print("Vendor Structure:")
print("  CLASS -> SYSTEM (XXX) -> COMPONENT (XXX) -> ASSEMBLY (XXX)")
print("  Example: TRAILER -> 72 -> 4 -> 69")
print()

print("Key Insight: Vendor uses SYSTEM-COMPONENT-ASSEMBLY")
print("             VMRS uses SYSTEM-ASSEMBLY-COMPONENT")
print("             The naming/order differs but structure is similar!")
print()

# ============================================================================
# PATTERN 6: MANUFACTURER CODES
# ============================================================================
print("\nPATTERN 6: MANUFACTURER/BRAND CODES")
print("-" * 80)

vendor_manufacturers = vendor_df['MANUFACTURER'].dropna().unique()
print(f"Unique manufacturers in vendor data: {len(vendor_manufacturers)}")
print(f"Top 15 manufacturers:")
for mfg, count in Counter(vendor_df['MANUFACTURER'].dropna()).most_common(15):
    print(f"  {mfg[:40]:40} | {count:5} parts")
print()

print("VMRS has Code Key 34 (5-char manufacturer codes)")
print("These can be used to identify specific brands/manufacturers")
print()

# ============================================================================
# SUMMARY: LINKING STRATEGIES
# ============================================================================
print("\n" + "="*80)
print("RECOMMENDED LINKING STRATEGIES")
print("="*80)
print()

print("1. DIRECT CODE MATCHING (Highest Confidence)")
print("   - Match Vendor SYSTEM+COMPONENT+ASSEMBLY to VMRS codes")
print(f"   - Current match rate: {vendor_9digit_matches/total_vendor_constructed*100:.1f}%")
print()

print("2. SYSTEM-LEVEL GROUPING (Medium Confidence)")
print(f"   - {len(common_systems)} common system codes found")
print("   - Group vendor parts by system and link to VMRS system descriptions")
print()

print("3. KEYWORD-BASED FUZZY MATCHING (Lower Confidence)")
print(f"   - {len(common_keywords)} shared keywords identified")
print("   - Use for parts without exact code matches")
print("   - Apply similarity scoring (TF-IDF, cosine similarity, etc.)")
print()

print("4. HIERARCHICAL TRAVERSAL")
print("   - Build tree structure for both datasets")
print("   - Link at system level, then drill down to assembly/component")
print()

print("5. HYBRID APPROACH (Recommended)")
print("   - Start with direct code matches")
print("   - Fall back to system-level grouping")
print("   - Use keyword matching for unmatched items")
print("   - Manual review for low-confidence matches")
print()

# ============================================================================
# SAVE ANALYSIS RESULTS
# ============================================================================
print("\nSaving detailed analysis files...")

# Save common systems
pd.DataFrame({
    'system_code': sorted(list(common_systems))
}).to_csv('eda/common_systems.csv', index=False)

# Save matched codes
matched_codes = vendor_with_codes[
    vendor_with_codes['constructed_code'].isin(vmrs_9digit)
][['PART', 'MANUFACTURER', 'DESCRIPTION', 'SYSTEM', 'COMPONENT', 'ASSEMBLY', 'constructed_code']]

matched_codes.to_csv('eda/vendor_vmrs_matched_codes.csv', index=False)

# Save top keywords
pd.DataFrame([
    {'keyword': k, 'vmrs_count': v[0], 'vendor_count': v[1]}
    for k, v in top_shared
]).to_csv('eda/shared_keywords.csv', index=False)

print("\nFiles saved:")
print("  - eda/common_systems.csv")
print("  - eda/vendor_vmrs_matched_codes.csv")
print("  - eda/shared_keywords.csv")
print()
print("Analysis complete!")
