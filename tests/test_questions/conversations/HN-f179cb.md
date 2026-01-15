# Test: HN-f179cb

## User

[TEST_ID: HN-f179cb] What is the hierarchy for VMRS code 174-002-020?

## Assistant

I'll help you find the hierarchy for VMRS code 174-002-020. Let me query the Neo4j database.

## Assistant

**Tool Call** (`mcp__neo4j-aura__get_neo4j_schema`):
```json
{}
```

## User

**Tool Result** (`toolu_01Xg4aXbsvJNUvBFrCxbSYDk`):
```json
{"result":[{"type":"text","text":"[{\"label\": \"System\", \"attributes\": {\"name\": \"STRING\", \"description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {}}, {\"label\": \"Assembly\", \"attributes\": {\"name\": \"STRING\", \"description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {\"PART_OF\": \"System\"}}, {\"label\": \"Component\", \"attributes\": {\"vmrs_official_description\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\", \"name\": \"STRING\", \"description\": \"STRING\", \"source\": \"STRING\"}, \"relationships\": {\"PART_OF\": \"Assembly\"}}, {\"label\": \"Vendor\", \"attributes\": {\"name\": \"STRING\", \"code\": \"STRING indexed\", \"updated_at\": \"INTEGER\"}, \"relationships\": {\"MANUFACTURES\": \"VendorPart\"}}, {\"label\": \"VendorPart\", \"attributes\": {\"manf_partmfr_name\": \"STRING\", \"component\": \"STRING\", \"system\": \"STRING\", \"manf_partnumber\": \"STRING\", \"part\": \"STRING indexed\", \"assembly\": \"STRING\", \"description\": \"STRING\", \"manf_partmfr\": \"STRING\", \"vmrs\": \"STRING\"}, \"relationships\": {\"MAPS_TO\": \"Component\"}}]","annotations":null,"_meta":null}]}
```

## Assistant

Now let me query for the specific VMRS code 174-002-020:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Search for Component with code 174-002-020\nMATCH (c:Component {code: '174-002-020'})-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)\nRETURN s.code AS system_code, s.name AS system_name,\n       a.code AS assembly_code, a.name AS assembly_name,\n       c.code AS component_code, c.name AS component_name, c.description AS component_description\n"
}
```

## User

**Tool Result** (`toolu_01X4FmhwZHruWhRrGW46ZuBN`):
```json
{"result":[{"type":"text","text":"[{\"system_code\": \"174\", \"system_name\": \"System 174\", \"assembly_code\": \"174-002\", \"assembly_name\": \"Assembly 174-002\", \"component_code\": \"174-002-020\", \"component_name\": \"MOUNTING BRACKET - STEP\", \"component_description\": \"Mounting Bracket - Step\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Let me also check if there are any vendor parts mapped to this component:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Check for vendor parts mapped to this component\nMATCH (vp:VendorPart)-[:MAPS_TO]->(c:Component {code: '174-002-020'})\nOPTIONAL MATCH (v:Vendor)-[:MANUFACTURES]->(vp)\nRETURN vp.manf_partmfr_name AS manufacturer, \n       vp.manf_partnumber AS part_number, \n       vp.description AS vendor_description,\n       v.name AS vendor_name\nLIMIT 5\n"
}
```

## User

**Tool Result** (`toolu_01ELKegz7kJY2fY4uqPJKNAP`):
```json
{"result":[{"type":"text","text":"[{\"manufacturer\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\", \"part_number\": \"3578797C1\", \"vendor_description\": \"BRACKET, STEP LH\", \"vendor_name\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\"}, {\"manufacturer\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\", \"part_number\": \"4004360C1\", \"vendor_description\": \"SUPPORT, STEP\", \"vendor_name\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\"}, {\"manufacturer\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\", \"part_number\": \"4004351C1\", \"vendor_description\": \"SUPPORT STEP\", \"vendor_name\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\"}, {\"manufacturer\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\", \"part_number\": \"3578796C1\", \"vendor_description\": \"BRACKET, STEP RH\", \"vendor_name\": \"NAVISTAR INTERNATIONAL TRANSPORTATION CORP.\"}]","annotations":null,"_meta":null}]}
```

## Assistant

Let me get more context about the parent System and Assembly:

## Assistant

**Tool Call** (`mcp__neo4j-aura__read_neo4j_cypher`):
```json
{
  "query": "\n// Get full details including descriptions\nMATCH (c:Component {code: '174-002-020'})-[:PART_OF]->(a:Assembly)-[:PART_OF]->(s:System)\nRETURN s.code AS system_code, s.name AS system_name, s.description AS system_description,\n       a.code AS assembly_code, a.name AS assembly_name, a.description AS assembly_description,\n       c.code AS component_code, c.name AS component_name, c.description AS component_description,\n       c.vmrs_official_description AS vmrs_official_description\n"
}
```

## User

**Tool Result** (`toolu_01KEMz7eT3pcAN9JwuuTS1Jf`):
```json
{"result":[{"type":"text","text":"[{\"system_code\": \"174\", \"system_name\": \"System 174\", \"system_description\": \"VMRS System 174\", \"assembly_code\": \"174-002\", \"assembly_name\": \"Assembly 174-002\", \"assembly_description\": \"VMRS Assembly 174-002\", \"component_code\": \"174-002-020\", \"component_name\": \"MOUNTING BRACKET - STEP\", \"component_description\": \"Mounting Bracket - Step\", \"vmrs_official_description\": \"Mounting Bracket - Step\"}]","annotations":null,"_meta":null}]}
```

## Assistant

## Answer for VMRS Code 174-002-020

**Exact Match Found:** Yes

### Hierarchy Path

**System 174** (neo4j)
→ **Assembly 174-002** (neo4j)
→ **Component 174-002-020: MOUNTING BRACKET - STEP** (neo4j)

### Details

- **Component Code:** 174-002-020
- **Component Name:** MOUNTING BRACKET - STEP
- **VMRS Official Description:** Mounting Bracket - Step
- **Assembly Code:** 174-002
- **System Code:** 174

### Vendor Parts Available

This component has 4 vendor parts mapped in the database, all from Navistar International Transportation Corp:
1. Part #3578797C1 - BRACKET, STEP LH (Left Hand)
2. Part #4004360C1 - SUPPORT, STEP
3. Part #4004351C1 - SUPPORT STEP
4. Part #3578796C1 - BRACKET, STEP RH (Right Hand)

### Reasoning

The VMRS code structure follows the standard three-level hierarchy:
- **System (174):** Top-level categorization
- **Assembly (174-002):** Mid-level grouping within the system
- **Component (174-002-020):** Specific part - a mounting bracket for steps

The vendor data confirms this is a step bracket/support component, with left-hand and right-hand variants available from Navistar.

### Potential Inaccuracies

The System and Assembly descriptions in the database are generic ("System 174", "Assembly 174-002") without detailed functional descriptions. System 174 likely relates to cab or body components based on the step mounting bracket context, but I cannot confirm the exact system category from the current data.

### Clarifying Question

What is the vehicle application or context where you need this mounting bracket? Knowing whether this is for a specific truck model or application would help confirm if the Navistar parts are the correct match for your needs.

