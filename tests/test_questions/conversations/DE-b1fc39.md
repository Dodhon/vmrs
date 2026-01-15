# Test: DE-b1fc39

## User

[TEST_ID: DE-b1fc39] What is the VMRS code for "CENTER SUPPORT BEARING"?

## Assistant

I'll help you find the VMRS code for "CENTER SUPPORT BEARING". Let me start by querying the Neo4j database.

First, let me get the schema to understand the structure:

## Assistant

**Tool Call** (`mcp__neo4j-aura__get_neo4j_schema`):
```json
{}
```

## User

**Tool Result** (`toolu_01GZUtH4dmtyZjbegiNV6CWQ`):
```json
{"result":[{"type":"text","text":"[{\"label\": \"System\", \"attributes\": {\"name\": \"STRING\", \"description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {}}, {\"label\": \"Assembly\", \"attributes\": {\"name\": \"STRING\", \"description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {\"PART_OF\": \"System\"}}, {\"label\": \"Component\", \"attributes\": {\"vmrs_official_description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\", \"name\": \"STRING\", \"description\": \"STRING\", \"source\": \"STRING\"}, \"relationships\": {\"PART_OF\": \"Assembly\"}}, {\"label\": \"Vendor\", \"attributes\": {\"name\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {\"MANUFACTURES\": \"VendorPart\"}}, {\"label\": \"VendorPart\", \"attributes\": {\"manf_partmfr_name\": \"STRING\", \"component\": \"STRING\", \"system\": \"STRING\", \"manf_partnumber\": \"STRING\", \"part\": \"STRING indexed\", \"assembly\": \"STRING\", \"description\": \"STRING\", \"manf_partmfr\": \"STRING\", \"vmrs\": \"STRING\"}, \"relationships\": {\"MAPS_TO\": \"Component\"}}]","annotations":null,"_meta":null}]}
```

## Assistant

Now let me search for "CENTER SUPPORT BEARING" in both Component names and VendorPart descriptions:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Search for CENTER SUPPORT BEARING in Component nodes\nMATCH (c:Component)\nWHERE c.name CONTAINS 'CENTER SUPPORT BEARING' \n   OR c.description CONTAINS 'CENTER SUPPORT BEARING'\n   OR c.vmrs_official_description CONTAINS 'CENTER SUPPORT BEARING'\nOPTIONAL MATCH (c)-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)\nRETURN c.code AS vmrs_code, \n       c.name AS component_name, \n       c.description AS component_description,\n       c.vmrs_official_description AS official_description,\n       a.code AS assembly_code, \n       a.name AS assembly_name,\n       s.code AS system_code, \n       s.name AS system_name\nORDER BY c.code\nLIMIT 10\n"
}
```

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Search for CENTER SUPPORT BEARING in VendorPart descriptions\nMATCH (vp:VendorPart)-[:MAPS_TO]->(c:Component)\nWHERE vp.description CONTAINS 'CENTER SUPPORT BEARING'\nOPTIONAL MATCH (c)-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)\nRETURN DISTINCT c.code AS vmrs_code, \n       c.name AS component_name,\n       vp.description AS vendor_description,\n       vp.vmrs AS vendor_vmrs,\n       a.code AS assembly_code, \n       a.name AS assembly_name,\n       s.code AS system_code, \n       s.name AS system_name\nORDER BY c.code\nLIMIT 10\n"
}
```

## User

**Tool Result** (`toolu_013DKhtqaLxTd1SWoQcCnrRg`):
```json
{"result":[{"type":"text","text":"[]","annotations":null,"_meta":null}]}
```

## User

**Tool Result** (`toolu_01MaEGJZrvst4CDpwqYV767j`):
```json
{"result":[{"type":"text","text":"[{\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CENTER SUPPORT BEARING\", \"vendor_vmrs\": \"024-002-005\", \"assembly_code\": \"024-002\", \"assembly_name\": \"DRIVE SHAFT, BEHIND MAIN TRANSMISSION\", \"system_code\": \"024\", \"system_name\": \"DRIVE SHAFTS\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Excellent! I found a match. Let me verify there are no other possible matches by searching more broadly:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Broader search for SUPPORT BEARING to find related components\nMATCH (c:Component)\nWHERE c.name CONTAINS 'SUPPORT BEARING' \n   OR c.description CONTAINS 'SUPPORT BEARING'\nOPTIONAL MATCH (c)-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)\nRETURN c.code AS vmrs_code, \n       c.name AS component_name, \n       c.description AS component_description,\n       a.name AS assembly_name,\n       s.name AS system_name\nORDER BY c.code\nLIMIT 10\n"
}
```

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Check VendorParts for SUPPORT BEARING variations\nMATCH (vp:VendorPart)-[:MAPS_TO]->(c:Component)\nWHERE vp.description CONTAINS 'SUPPORT BEARING'\nOPTIONAL MATCH (c)-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)\nRETURN DISTINCT c.code AS vmrs_code, \n       c.name AS component_name,\n       COUNT(vp) AS vendor_part_count,\n       a.name AS assembly_name,\n       s.name AS system_name\nORDER BY c.code\nLIMIT 10\n"
}
```

## User

**Tool Result** (`toolu_01FqHqF4DZXSLsiSGchgSmyM`):
```json
{"result":[{"type":"text","text":"[]","annotations":null,"_meta":null}]}
```

## User

**Tool Result** (`toolu_01BG8zPduM4uta5cFMLuBywL`):
```json
{"result":[{"type":"text","text":"[{\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_part_count\": 2, \"assembly_name\": \"DRIVE SHAFT, BEHIND MAIN TRANSMISSION\", \"system_name\": \"DRIVE SHAFTS\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Perfect! Let me get a few more details about this component and check if there are any other bearing-related components in the drive shaft system:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Get all components in the DRIVE SHAFT assembly that contain BEARING\nMATCH (c:Component)-[:PART_OF]->(a:Assembly {code: '024-002'})-[:PART_OF]->(s:System)\nWHERE c.name CONTAINS 'BEARING' OR c.description CONTAINS 'BEARING'\nRETURN c.code AS vmrs_code, \n       c.name AS component_name, \n       c.description AS component_description\nORDER BY c.code\n"
}
```

## User

**Tool Result** (`toolu_017AUo1Wqc68fEtPGxxNQkj8`):
```json
{"result":[{"type":"text","text":"[{\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"component_description\": \"Bearing Assembly - Drive Shaft\"}, {\"vmrs_code\": \"024-002-008\", \"component_name\": \"SUPPORT ASSEMBLY - BEARING, DRIVE SHAFT\", \"component_description\": \"Support Assembly - Bearing, Drive Shaft\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Interesting! There are two related components. Let me check if the second one (024-002-008) also has vendor parts mapped to it:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Check vendor parts for both bearing components\nMATCH (vp:VendorPart)-[:MAPS_TO]->(c:Component)\nWHERE c.code IN ['024-002-005', '024-002-008']\nRETURN c.code AS vmrs_code, \n       c.name AS component_name,\n       vp.description AS vendor_description,\n       vp.manf_partmfr_name AS manufacturer\nORDER BY c.code, vp.description\n"
}
```

## User

**Tool Result** (`toolu_01KwYWtuWwjt5jUpSgbq3kCu`):
```json
{"result":[{"type":"text","text":"[{\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"ASSY, CENTER BEARING\", \"manufacturer\": \"SPICER AXLE-TRANS DIVS DANA CORP.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, CARRIER\", \"manufacturer\": \"VOLVO TRUCKS NORTH AMERICA, INC.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, CENTER\", \"manufacturer\": \"SPICER AXLE-TRANS DIVS DANA CORP.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, CENTRE, DRIVELINE\", \"manufacturer\": \"MERITOR INC.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, CENTRE, SUPPORT\", \"manufacturer\": \"MERITOR INC.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, DRIVE SHAFT, CTR SPT\", \"manufacturer\": \"SPICER AXLE-TRANS DIVS DANA CORP.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, DRIVESHAFT, CENTRE\", \"manufacturer\": \"SPICER AXLE-TRANS DIVS DANA CORP.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"BEARING, SELF ALIGNING CARRIER\", \"manufacturer\": \"ATRO ENGINEERED SYSTEMS, INC,\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CARRIER BEARING\", \"manufacturer\": \"FREIGHTLINER CORPORATION\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CARRIER BEARING\", \"manufacturer\": \"VOLVO TRUCKS NORTH AMERICA, INC.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CARRIER, BEARING, DRIVELINE\", \"manufacturer\": \"MERITOR INC.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CENTER BUSHING\", \"manufacturer\": \"SPICER AXLE-TRANS DIVS DANA CORP.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CENTER SUPPORT BEARING\", \"manufacturer\": \"VOLVO TRUCKS NORTH AMERICA, INC.\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"CENTER SUPPORT BEARING\", \"manufacturer\": \"ANCHOR PARTS\"}, {\"vmrs_code\": \"024-002-005\", \"component_name\": \"BEARING ASSEMBLY - DRIVE SHAFT\", \"vendor_description\": \"HOUSING, CENTER BEARING\", \"manufacturer\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\"}, {\"vmrs_code\": \"024-002-008\", \"component_name\": \"SUPPORT ASSEMBLY - BEARING, DRIVE SHAFT\", \"vendor_description\": \"CENTER SUPPORT BRGS\", \"manufacturer\": \"NEAPCO, INC.\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Perfect! Now I have comprehensive information. Let me provide you with the answer:

---

## Answer

**VMRS Code: 024-002-005**

### Top 3 Most Likely Matches:

**1. EXACT MATCH: 024-002-005 - BEARING ASSEMBLY - DRIVE SHAFT** ✓
- **Hierarchy:** System 024 (DRIVE SHAFTS) → Assembly 024-002 (DRIVE SHAFT, BEHIND MAIN TRANSMISSION) → Component 024-002-005
- **Source:** (neo4j)
- **Confidence:** VERY HIGH - Exact match found in vendor part descriptions

**2. POSSIBLE ALTERNATIVE: 024-002-008 - SUPPORT ASSEMBLY - BEARING, DRIVE SHAFT**
- **Hierarchy:** System 024 (DRIVE SHAFTS) → Assembly 024-002 (DRIVE SHAFT, BEHIND MAIN TRANSMISSION) → Component 024-002-008
- **Source:** (neo4j)
- **Confidence:** LOW - One vendor part describes this as "CENTER SUPPORT BRGS" (NEAPCO, INC.)

**3. No third distinct match found** - Only these two components exist in the drive shaft bearing category.

---

### Reasoning for Recommendation:

**024-002-005 is the correct answer** because:
1. Two vendor parts (Volvo and Anchor Parts) use the **exact term "CENTER SUPPORT BEARING"** for this VMRS code
2. Multiple other vendors use highly similar terminology:
   - "BEARING, CENTRE, SUPPORT" (Meritor)
   - "BEARING, CENTER" (Spicer/Dana)
   - "ASSY, CENTER BEARING" (Spicer/Dana)
   - "CARRIER BEARING" (Freightliner, Volvo)
3. The component is part of the drive shaft system, which is the typical location for center support bearings
4. 15 different vendor parts from major manufacturers (Meritor, Dana/Spicer, Volvo, Freightliner, Navistar) all map to this code

---

### Why This Recommendation May Be Incorrect:

1. **Semantic ambiguity:** The VMRS official name "BEARING ASSEMBLY - DRIVE SHAFT" is generic and could theoretically include multiple bearing types
2. **Component vs. Support distinction:** Code 024-002-008 specifically mentions "SUPPORT ASSEMBLY" which might be more precise if you're looking for the entire support bracket/assembly rather than just the bearing itself
3. **Regional terminology:** "Center support bearing" may be vendor-specific slang that doesn't perfectly align with VMRS nomenclature

---

### Clarifying Question:

**Are you looking for:**
1. Just the bearing component itself (likely 024-002-005), OR
2. The complete support bracket/housing assembly that holds the bearing (possibly 024-002-008)?

This distinction matters because in parts catalogs, these are sometimes listed as separate items - the bearing insert vs. the complete mounted assembly.

