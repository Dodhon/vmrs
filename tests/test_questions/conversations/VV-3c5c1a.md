# Test: VV-3c5c1a

## User

[TEST_ID: VV-3c5c1a] Is 026-015-095 a valid VMRS code?

## Assistant

I'll check if 026-015-095 is a valid VMRS code by querying the Neo4j database.

First, let me get the schema to understand the structure.

## Assistant

**Tool Call** (`mcp__neo4j-aura__get_neo4j_schema`):
```json
{}
```

## User

**Tool Result** (`toolu_01DWK3tuHnNRZiCskQcxSzp4`):
```json
{"result":[{"type":"text","text":"[{\"label\": \"System\", \"attributes\": {\"name\": \"STRING\", \"description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {}}, {\"label\": \"Assembly\", \"attributes\": {\"name\": \"STRING\", \"description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {\"PART_OF\": \"System\"}}, {\"label\": \"Component\", \"attributes\": {\"vmrs_official_description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\", \"name\": \"STRING\", \"description\": \"STRING\", \"source\": \"STRING\"}, \"relationships\": {\"PART_OF\": \"Assembly\"}}, {\"label\": \"Vendor\", \"attributes\": {\"name\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {\"MANUFACTURES\": \"VendorPart\"}}, {\"label\": \"VendorPart\", \"attributes\": {\"manf_partmfr_name\": \"STRING\", \"component\": \"STRING\", \"system\": \"STRING\", \"manf_partnumber\": \"STRING\", \"part\": \"STRING indexed\", \"assembly\": \"STRING\", \"description\": \"STRING\", \"manf_partmfr\": \"STRING\", \"vmrs\": \"STRING\"}, \"relationships\": {\"MAPS_TO\": \"Component\"}}]","annotations":null,"_meta":null}]}
```

## Assistant

Now let me search for this code. Based on the VMRS structure (XXX-XXX-XXX format), this appears to be a complete System-Assembly-Component code. Let me check all three levels:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Check System level (026)\nMATCH (s:System {code: '026'})\nOPTIONAL MATCH (s)<-[:PART_OF]-(a:Assembly {code: '026-015'})\nOPTIONAL MATCH (a)<-[:PART_OF]-(c:Component {code: '026-015-095'})\nRETURN \n  s.code AS system_code,\n  s.name AS system_name,\n  s.description AS system_description,\n  a.code AS assembly_code,\n  a.name AS assembly_name,\n  a.description AS assembly_description,\n  c.code AS component_code,\n  c.name AS component_name,\n  c.description AS component_description,\n  c.vmrs_official_description AS component_official_desc\n"
}
```

## User

**Tool Result** (`toolu_013sHU2abTU3L3e7tDj22oPZ`):
```json
{"result":[{"type":"text","text":"[{\"system_code\": \"026\", \"system_name\": \"System 026\", \"system_description\": \"VMRS System 026\", \"assembly_code\": \"026-015\", \"assembly_name\": \"Assembly 026-015\", \"assembly_description\": \"VMRS Assembly 026-015\", \"component_code\": \"026-015-095\", \"component_name\": \"SWITCH - HILL ASSIST, AUTOMATED TRANSMISSION\", \"component_description\": \"Switch - Hill Assist Automated Transmission / Switch - Hill Assist, Automated Transmission\", \"component_official_desc\": \"Switch - Hill Assist Automated Transmission / Switch - Hill Assist, Automated Transmission\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Perfect! Let me also check if there are any vendor parts mapped to this component:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Check for vendor parts mapped to this component\nMATCH (vp:VendorPart)-[:MAPS_TO]->(c:Component {code: '026-015-095'})\nOPTIONAL MATCH (v:Vendor)-[:MANUFACTURES]->(vp)\nRETURN \n  v.name AS vendor_name,\n  vp.manf_partmfr_name AS manufacturer,\n  vp.manf_partnumber AS part_number,\n  vp.description AS vendor_description\nLIMIT 5\n"
}
```

## User

**Tool Result** (`toolu_01L89wJp8RaRX9QhrjWN4DG4`):
```json
{"result":[{"type":"text","text":"[{\"vendor_name\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\", \"manufacturer\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\", \"part_number\": \"4102452C2\", \"vendor_description\": \"SWITCH, MULTIPLEX ,HILL START\"}]","annotations":null,"_meta":null}]}
```

## Assistant

## Answer

**YES, 026-015-095 is a valid VMRS code.**

### Hierarchy Path
- **System 026**: VMRS System 026 (neo4j)
- **Assembly 026-015**: VMRS Assembly 026-015 (neo4j)
- **Component 026-015-095**: SWITCH - HILL ASSIST, AUTOMATED TRANSMISSION (neo4j)

### Component Details
- **VMRS Code**: 026-015-095
- **Name**: SWITCH - HILL ASSIST, AUTOMATED TRANSMISSION (neo4j)
- **Official Description**: Switch - Hill Assist Automated Transmission / Switch - Hill Assist, Automated Transmission (neo4j)

### Vendor Data Available
Yes, this component has vendor parts mapped to it:
- **Vendor**: NAVISTAR INTERNATIONAL TRANSPORTATION CORP. (neo4j)
- **Part Number**: 4102452C2 (neo4j)
- **Description**: SWITCH, MULTIPLEX ,HILL START (neo4j)

### Reasoning
This is a valid three-level VMRS code found in the knowledge graph with complete hierarchy information. The code follows the standard XXX-XXX-XXX format for System-Assembly-Component and has both VMRS standard definitions and vendor part mappings.

### Confidence
This is an exact match with high confidence. The code exists in the Neo4j database with full metadata.

### Potential Issues
None identified. The code is properly structured and has complete data.

### Clarifying Questions
- Are you looking for additional vendors that supply this part?
- Do you need cross-reference information for compatible parts?

