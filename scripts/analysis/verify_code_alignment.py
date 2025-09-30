import pandas as pd
import re
from collections import defaultdict

# Load datasets
vmrs_df = pd.read_csv("csv data/VMRS_COMPLETE_v20_MASTER.csv")
vendor_df = pd.read_csv("vendor data/Master Parts list for Richard 06.25.25 (1).csv")
matched_df = pd.read_csv("eda/vendor_vmrs_matched_codes.csv")

print("="*80)
print("DETAILED CODE ALIGNMENT VERIFICATION")
print("="*80)
print()

# ============================================================================
# VERIFY: What does the 93.7% match mean?
# ============================================================================
print("CLARIFICATION: What is the 93.7% match?")
print("-" * 80)

print(f"Total vendor parts: {len(vendor_df):,}")
print(f"Vendor parts with numeric SYSTEM & COMPONENT: {len(matched_df):,}")
print(f"Percentage with numeric codes: {len(matched_df)/len(vendor_df)*100:.1f}%")
print()

# Check if constructed codes exist in VMRS
vmrs_codes = set(vmrs_df['code_9d'].dropna())
print(f"Total unique VMRS 9-digit codes: {len(vmrs_codes):,}")
print()

matched_codes = matched_df['constructed_code'].unique()
print(f"Unique vendor constructed codes: {len(matched_codes):,}")
print()

# Verify actual matches
actually_in_vmrs = [code for code in matched_codes if code in vmrs_codes]
print(f"Vendor codes that exist in VMRS: {len(actually_in_vmrs):,}")
print(f"Match rate: {len(actually_in_vmrs)/len(matched_codes)*100:.1f}%")
print()

print("INTERPRETATION:")
print("  93.7% = Out of 18,327 vendor parts with complete numeric codes,")
print("          17,168 have codes that exist in the VMRS standard")
print()

# ============================================================================
# FIND PERFECT SUBSETS FOR PoC
# ============================================================================
print("\n" + "="*80)
print("FINDING PERFECT SUBSETS FOR PROOF OF CONCEPT")
print("="*80)
print()

# Group matched parts by system
matched_df['system'] = matched_df['constructed_code'].str[:3]
system_counts = matched_df['system'].value_counts()

print("Top 20 systems by matched part count:")
print("-" * 80)
for sys, count in system_counts.head(20).items():
    # Get VMRS system name
    vmrs_sys_name = vmrs_df[vmrs_df['system'] == sys]['description'].iloc[0] if len(vmrs_df[vmrs_df['system'] == sys]) > 0 else 'Unknown'
    # Get first few words
    sys_name_short = ' '.join(str(vmrs_sys_name).split()[:5])
    print(f"  System {sys}: {count:5} parts | {sys_name_short}")
print()

# ============================================================================
# DEEP DIVE: Compare descriptions for top systems
# ============================================================================
print("\n" + "="*80)
print("DESCRIPTION ALIGNMENT ANALYSIS")
print("="*80)
print()

def similarity_score(str1, str2):
    """Simple word overlap similarity"""
    if pd.isna(str1) or pd.isna(str2):
        return 0.0
    words1 = set(re.findall(r'\b\w+\b', str(str1).lower()))
    words2 = set(re.findall(r'\b\w+\b', str(str2).lower()))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union) if union else 0.0

# Analyze top 3 systems for description alignment
top_systems = system_counts.head(3).index.tolist()

for sys in top_systems:
    print(f"\nSystem {sys} Analysis:")
    print("-" * 80)
    
    # Get vendor parts for this system
    sys_vendor = matched_df[matched_df['system'] == sys].head(20)
    
    # Get VMRS system description
    vmrs_sys = vmrs_df[vmrs_df['system'] == sys].iloc[0] if len(vmrs_df[vmrs_df['system'] == sys]) > 0 else None
    if vmrs_sys is not None:
        print(f"VMRS System Name: {vmrs_sys['description']}")
    print()
    
    similarities = []
    examples = []
    
    for idx, row in sys_vendor.iterrows():
        vendor_desc = row['DESCRIPTION']
        code = row['constructed_code']
        
        # Find matching VMRS description
        vmrs_match = vmrs_df[vmrs_df['code_9d'] == code]
        if len(vmrs_match) > 0:
            vmrs_desc = vmrs_match.iloc[0]['description']
            sim = similarity_score(vendor_desc, vmrs_desc)
            similarities.append(sim)
            
            if len(examples) < 5:
                examples.append({
                    'code': code,
                    'vendor': str(vendor_desc)[:50],
                    'vmrs': str(vmrs_desc)[:50],
                    'similarity': sim
                })
    
    if similarities:
        avg_sim = sum(similarities) / len(similarities)
        print(f"Average description similarity: {avg_sim:.2f}")
        print(f"High similarity matches (>0.3): {sum(1 for s in similarities if s > 0.3)} / {len(similarities)}")
        print()
        
        print("Sample comparisons:")
        for ex in examples:
            print(f"  {ex['code']} (sim: {ex['similarity']:.2f})")
            print(f"    Vendor: {ex['vendor']}")
            print(f"    VMRS:   {ex['vmrs']}")
            print()

# ============================================================================
# IDENTIFY BEST POC SUBSETS
# ============================================================================
print("\n" + "="*80)
print("RECOMMENDED POC SUBSETS")
print("="*80)
print()

# Strategy 1: Find systems with high description alignment
system_quality = {}
for sys in system_counts.head(10).index:
    sys_parts = matched_df[matched_df['system'] == sys]
    similarities = []
    
    for idx, row in sys_parts.head(50).iterrows():
        code = row['constructed_code']
        vendor_desc = row['DESCRIPTION']
        
        vmrs_match = vmrs_df[vmrs_df['code_9d'] == code]
        if len(vmrs_match) > 0:
            vmrs_desc = vmrs_match.iloc[0]['description']
            sim = similarity_score(vendor_desc, vmrs_desc)
            similarities.append(sim)
    
    if similarities:
        avg_sim = sum(similarities) / len(similarities)
        system_quality[sys] = {
            'count': len(sys_parts),
            'avg_similarity': avg_sim,
            'high_quality': sum(1 for s in similarities if s > 0.3)
        }

# Sort by quality
sorted_systems = sorted(system_quality.items(), 
                        key=lambda x: (x[1]['avg_similarity'], x[1]['count']), 
                        reverse=True)

print("Top 5 Systems for PoC (by description alignment):")
print("-" * 80)
for i, (sys, quality) in enumerate(sorted_systems[:5], 1):
    vmrs_name = vmrs_df[vmrs_df['system'] == sys]['description'].iloc[0] if len(vmrs_df[vmrs_df['system'] == sys]) > 0 else 'Unknown'
    sys_name_short = ' '.join(str(vmrs_name).split()[:6])
    print(f"\n{i}. System {sys}: {sys_name_short}")
    print(f"   - Part count: {quality['count']:,}")
    print(f"   - Avg description similarity: {quality['avg_similarity']:.2f}")
    print(f"   - High-quality matches: {quality['high_quality']}")

print()

# ============================================================================
# EXPORT POC DATASET
# ============================================================================
print("\n" + "="*80)
print("CREATING POC DATASET")
print("="*80)
print()

# Select best system for PoC
if sorted_systems:
    best_sys = sorted_systems[0][0]
    
    print(f"Selected System: {best_sys}")
    
    # Get all vendor parts for this system
    poc_vendor = matched_df[matched_df['system'] == best_sys].copy()
    
    # Merge with VMRS data
    poc_data = []
    for idx, row in poc_vendor.iterrows():
        code = row['constructed_code']
        vmrs_match = vmrs_df[vmrs_df['code_9d'] == code]
        
        if len(vmrs_match) > 0:
            vmrs_row = vmrs_match.iloc[0]
            similarity = similarity_score(row['DESCRIPTION'], vmrs_row['description'])
            
            poc_data.append({
                'vendor_part': row['PART'],
                'vendor_manufacturer': row['MANUFACTURER'],
                'vendor_description': row['DESCRIPTION'],
                'vmrs_code': code,
                'vmrs_system': vmrs_row['system'],
                'vmrs_subcode': vmrs_row['subcode'],
                'vmrs_description': vmrs_row['description'],
                'description_similarity': similarity,
                'quality': 'HIGH' if similarity > 0.3 else 'MEDIUM' if similarity > 0.15 else 'LOW'
            })
    
    poc_df = pd.DataFrame(poc_data)
    poc_df.to_csv('eda/poc_dataset.csv', index=False)
    
    print(f"✓ Created PoC dataset: {len(poc_df)} parts")
    print(f"  File: eda/poc_dataset.csv")
    print()
    
    # Summary stats
    print("Quality breakdown:")
    print(f"  HIGH quality (sim > 0.30): {len(poc_df[poc_df['quality'] == 'HIGH']):,} parts")
    print(f"  MEDIUM quality (0.15-0.30): {len(poc_df[poc_df['quality'] == 'MEDIUM']):,} parts")
    print(f"  LOW quality (< 0.15): {len(poc_df[poc_df['quality'] == 'LOW']):,} parts")
    print()
    
    # Show some high-quality examples
    print("\nHigh-quality examples (top 10):")
    print("-" * 80)
    high_quality = poc_df[poc_df['quality'] == 'HIGH'].sort_values('description_similarity', ascending=False).head(10)
    for idx, row in high_quality.iterrows():
        print(f"\n{row['vmrs_code']} (sim: {row['description_similarity']:.2f})")
        print(f"  Part: {row['vendor_part']}")
        print(f"  Vendor: {row['vendor_description'][:60]}")
        print(f"  VMRS:   {row['vmrs_description'][:60]}")

# ============================================================================
# ALTERNATIVE: Create subset with PERFECT alignment
# ============================================================================
print("\n\n" + "="*80)
print("ALTERNATIVE: PERFECT ALIGNMENT SUBSET")
print("="*80)
print()

# Find parts where vendor description has significant overlap with VMRS
perfect_matches = []
for idx, row in matched_df.head(1000).iterrows():  # Check first 1000 for speed
    code = row['constructed_code']
    vmrs_match = vmrs_df[vmrs_df['code_9d'] == code]
    
    if len(vmrs_match) > 0:
        vmrs_desc = vmrs_match.iloc[0]['description']
        sim = similarity_score(row['DESCRIPTION'], vmrs_desc)
        
        if sim > 0.4:  # High threshold
            perfect_matches.append({
                'vendor_part': row['PART'],
                'vendor_manufacturer': row['MANUFACTURER'],
                'vendor_description': row['DESCRIPTION'],
                'vmrs_code': code,
                'vmrs_description': vmrs_desc,
                'similarity': sim
            })

if perfect_matches:
    perfect_df = pd.DataFrame(perfect_matches)
    perfect_df.to_csv('eda/perfect_alignment_poc.csv', index=False)
    
    print(f"✓ Created perfect alignment dataset: {len(perfect_df)} parts")
    print(f"  File: eda/perfect_alignment_poc.csv")
    print(f"  Criteria: Description similarity > 0.40")
    print()
    
    print("Top 10 examples:")
    print("-" * 80)
    for idx, row in perfect_df.head(10).iterrows():
        print(f"\n{row['vmrs_code']} (sim: {row['similarity']:.2f})")
        print(f"  Vendor: {row['vendor_description'][:60]}")
        print(f"  VMRS:   {row['vmrs_description'][:60]}")

print("\n" + "="*80)
print("Analysis complete!")
print("="*80)
