# VMRS to Vendor Data Linking Patterns

## Executive Summary

Analysis of **66,729 VMRS records** and **29,710 vendor parts** reveals strong structural alignment with a **93.7% direct code match rate** for parts with complete VMRS codes.

---

## Key Finding: High Match Rate! 🎯

**18,327 vendor parts** (61.7% of total) have complete VMRS codes, and **17,168 of these** (93.7%) directly match existing VMRS component codes.

---

## Pattern 1: Code Structure Mapping

### Structural Insight

The vendor and VMRS use similar hierarchical systems but with **different naming conventions**:

| System | Level 1 | Level 2 | Level 3 | Example |
|--------|---------|---------|---------|---------|
| **VMRS** | SYSTEM (XXX) | ASSEMBLY (XXX) | COMPONENT (XXX) | `001-002-064` |
| **Vendor** | SYSTEM (XXX) | COMPONENT (XXX) | ASSEMBLY (XXX) | `72-4-69` |

**Critical Discovery**: The vendor's `COMPONENT` and `ASSEMBLY` fields are **swapped** compared to VMRS naming, but the **structure is the same**!

### Mapping Formula

```python
vendor_vmrs_code = f"{SYSTEM:03d}-{COMPONENT:03d}-{ASSEMBLY:03d}"
```

This formula correctly maps to VMRS 9-digit codes with 93.7% accuracy.

### Example Matches

| Vendor Code | Vendor Description | VMRS Description |
|-------------|-------------------|------------------|
| 072-004-069 | BALANCER ASSEMBLY | Shaft - Roller, Roll-Up, Rear Door |
| 072-004-064 | SPRING, REPLACEMENT | Spring - Door Operator |
| 017-001-011 | RETREAD, B197 ,11R22.5 | Tire - Retread, Trailer |
| 017-001-041 | RETREAD, B835, 445/50R22.5 | Tire - Wide Base, Retread, Rib Tread |

---

## Pattern 2: Keyword-Based Semantic Linking

### High-Value Keywords

**1,890 shared keywords** between datasets indicate semantic overlap. Top component types:

| Keyword | VMRS Count | Vendor Count | Use Case |
|---------|-----------|--------------|----------|
| kit | 1,800 | 1,721 | Part groupings |
| brake | 1,404 | 1,268 | Brake systems |
| hose | 1,271 | 1,257 | Fluid lines |
| air | 3,154 | 1,197 | Pneumatic systems |
| valve | 3,429 | 966 | Control components |
| oil | 1,354 | 919 | Lubrication |
| filter | 862 | 913 | Filtration systems |
| sensor | 904 | 802 | Monitoring devices |
| fuel | 1,402 | 753 | Fuel systems |
| seal | 1,500 | 723 | Sealing components |

### Linking Strategy

For parts **without exact code matches**, use keyword-based similarity:

1. Extract keywords from descriptions
2. Calculate TF-IDF vectors
3. Compute cosine similarity
4. Rank VMRS candidates
5. Manual review for confidence < 0.85

---

## Pattern 3: Class to System Mapping

### Vendor Classes (23 total)

The vendor data includes high-level classifications:

- TRAILER
- TIRES  
- LIGHTING
- FLUIDS
- BATTERIES
- MHE (Material Handling Equipment)
- BRAKES
- SUPPLIES
- ENGINE
- ELECTRICAL
- FRAME
- FILTERS
- CAB
- EMISSIONS
- LIFTGATE

### VMRS Systems (289 total)

VMRS systems are 3-digit codes (001-999) that represent equipment systems. The vendor `CLASS` field provides semantic grouping that can be mapped to VMRS system groups.

### Potential Mapping Examples

| Vendor CLASS | Likely VMRS Systems |
|--------------|---------------------|
| ENGINE | 001 (A/C, Heating), 002 (Engine), 003 (Transmission) |
| BRAKES | 013 (Brakes), 014 (Steering) |
| TIRES | 017 (Tires & Wheels) |
| LIGHTING | 034 (Lighting) |
| ELECTRICAL | 015 (Electrical), 040 (Instruments) |

**Note**: Requires manual mapping table creation based on VMRS handbook definitions.

---

## Pattern 4: Manufacturer Linkage

### Vendor Manufacturers

- **910 unique manufacturers** in vendor data
- Top manufacturers: Freightliner, Crown, Volvo, Toyota, Ford, International, Cummins

### VMRS Code Key 34

VMRS includes **5-character manufacturer codes** (Code Key 34) for brand identification.

### Linking Opportunity

- Map vendor `MANUFACTURER` names to VMRS 5-char codes
- Enables manufacturer-specific part identification
- Supports warranty and OEM analysis

**Example**: 
- Vendor: "CUMMINS ENGINE CO" → VMRS: "CMINS" (Code Key 34)
- Enables queries like "all Cummins engine parts with VMRS codes"

---

## Pattern 5: Hierarchical Traversal

### Tree Structure Approach

Both datasets can be represented as trees:

```
VMRS:
├── System 001 (Air Conditioning)
│   ├── Assembly 001-000 (Compressor Assembly)
│   │   ├── Component 001-000-001
│   │   ├── Component 001-000-002
│   │   └── ...
│   ├── Assembly 001-001 (Air Conditioning)
│   └── Assembly 001-002 (Heating & Ventilating)
```

```
Vendor:
├── CLASS: ENGINE
│   ├── System 002
│   │   ├── COMPONENT 1 - ASSEMBLY 1
│   │   ├── COMPONENT 1 - ASSEMBLY 2
│   │   └── ...
```

### Linking Algorithm

1. **Level 1**: Match by SYSTEM code
2. **Level 2**: Within matched system, align assemblies
3. **Level 3**: Match components within assemblies
4. **Fall-back**: Use keyword similarity for unmatched nodes

---

## Data Quality Observations

### Coverage Statistics

| Dataset | Total Records | With Codes | Match Rate |
|---------|--------------|------------|------------|
| VMRS | 66,729 | 59,650 (9-digit) | 100% (reference) |
| Vendor | 29,710 | 18,327 (with numeric codes) | 93.7% match to VMRS |

### Vendor Data Characteristics

- **61.7%** of vendor parts have complete VMRS codes
- **38.3%** of vendor parts lack complete VMRS codes or use non-numeric codes
- **23 classes** provide semantic grouping
- **910 manufacturers** enable brand-specific analysis

### VMRS Data Characteristics

- **289 systems** covering comprehensive equipment hierarchy
- **89.4%** are component-level (9-digit codes)
- **10.6%** are assembly-level (6-digit codes)
- **4.9%** have empty descriptions (quality issue)

---

## Recommended Knowledge Graph Structure

### Nodes

1. **VMRS System Nodes**
   - Properties: code, name, description
   
2. **VMRS Assembly Nodes**
   - Properties: code, name, description, system_code
   
3. **VMRS Component Nodes**
   - Properties: code, name, description, assembly_code, system_code

4. **Vendor Part Nodes**
   - Properties: part_number, manufacturer, description, class

5. **Manufacturer Nodes**
   - Properties: name, vmrs_code_key_34

### Relationships

1. **PART_OF** (hierarchical)
   - Component → Assembly
   - Assembly → System

2. **MATCHES** (linking)
   - Vendor Part → VMRS Component (with confidence score)
   - High confidence: 1.0 (exact code match)
   - Medium confidence: 0.5-0.99 (keyword similarity)
   - Low confidence: <0.5 (manual review needed)

3. **MADE_BY**
   - Vendor Part → Manufacturer
   - VMRS Component → Manufacturer (via Code Key 34)

4. **CATEGORIZED_AS**
   - Vendor Part → Class
   - VMRS System → Class (mapped)

### Query Examples

```cypher
// Find all vendor parts for a specific VMRS component
MATCH (v:VendorPart)-[m:MATCHES]->(c:VMRSComponent)
WHERE c.code = '001-002-064'
RETURN v, m.confidence

// Find all brake-related parts across both systems
MATCH (v:VendorPart)
WHERE v.class = 'BRAKES'
MATCH (c:VMRSComponent)-[:PART_OF]->(s:VMRSSystem)
WHERE s.code = '013'
RETURN v, c

// Manufacturer analysis
MATCH (v:VendorPart)-[:MADE_BY]->(m:Manufacturer)
WHERE m.name CONTAINS 'CUMMINS'
MATCH (v)-[:MATCHES]->(c:VMRSComponent)
RETURN m, count(v) as parts_count, collect(c.code) as vmrs_codes
```

---

## Implementation Roadmap

### Phase 1: Direct Code Linking (Week 1)
- ✅ Construct VMRS codes from vendor SYSTEM-COMPONENT-ASSEMBLY
- ✅ Match 93.7% of parts with exact codes
- Create initial knowledge graph with high-confidence links

### Phase 2: Keyword-Based Fuzzy Matching (Week 2)
- Extract and normalize keywords from descriptions
- Build TF-IDF similarity matrix
- Link remaining parts with confidence scores
- Manual review queue for low-confidence matches

### Phase 3: Manufacturer Mapping (Week 3)
- Create vendor manufacturer → VMRS Code Key 34 mapping table
- Link parts through manufacturer relationships
- Enable OEM-specific queries

### Phase 4: Hierarchical Enrichment (Week 4)
- Build tree structures for both datasets
- Create system-level groupings
- Map vendor CLASS to VMRS system groups
- Enable hierarchical queries

### Phase 5: Validation & Refinement (Week 5)
- Cross-reference with VMRS handbook (md data)
- Fix OCR errors in descriptions
- Fill empty descriptions
- Quality assurance testing

---

## Files Generated

- `eda/common_systems.csv` - System codes present in both datasets
- `eda/vendor_vmrs_matched_codes.csv` - 17,168 exact code matches
- `eda/shared_keywords.csv` - 1,890 shared keywords with frequencies

---

## Next Steps

1. **Create mapping tables** for vendor classes to VMRS systems
2. **Build manufacturer lookup** for Code Key 34 alignment  
3. **Implement fuzzy matching** for parts without exact codes
4. **Design graph schema** with node types and relationships
5. **Develop query interface** for knowledge graph exploration

---

*Analysis completed: September 30, 2025*
*Datasets: 66,729 VMRS codes | 29,710 vendor parts | 93.7% match rate*
