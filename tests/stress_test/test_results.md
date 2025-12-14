# Stress Test Results - Neo4j MCP Chatbot

**Test Date:** 2025-12-13
**Tester:** Claude Code
**Interface:** Claude Desktop + Neo4j MCP
**Total Tests Planned:** 60 (10 per category x 6 categories)

---

## Test Classification Legend

- **PASS**: Correct VMRS code returned
- **PARTIAL**: Correct system/assembly but wrong component
- **FAIL**: Wrong VMRS code returned
- **NOT_FOUND_OK**: System correctly said "not found" for missing data
- **CLARIFIED**: System asked appropriate clarifying question
- **ERROR**: System error or unexpected behavior

---

## Data Quality Tests (10 samples)

Testing: Abbreviations, spelling errors, punctuation, embedded codes, truncated text

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| DQ-001 | What is the VMRS code for CONDENSER-A/C,55T,815CC? | 001-001-062 | _Testing_ | | Complex abbreviation with embedded specs |
| DQ-002 | What is the VMRS code for DRYER, A/C - W/ WAFER DYE? | 001-001-065 | _Testing_ | | Multiple abbreviations |
| DQ-011 | What is the VMRS code for CONDENSOR, AC? | 001-001-062 | _Testing_ | | Spelling error: CONDENSOR |
| DQ-013 | What is the VMRS code for WINSHIELD? | 002-024-001 | _Testing_ | | Spelling error: WINSHIELD |
| DQ-019 | What is the VMRS code for WASHER,SEALING,A/C #12? | 001-001-063 | _Testing_ | | Heavy punctuation |
| DQ-026 | What is the VMRS code for CONDENSER-AC, 51T, 1009CC? | 001-001-062 | _Testing_ | | Embedded specifications |
| DQ-031 | What is the VMRS code for HEATER HOSE .375 X 600? | 001-002-022 | _Testing_ | | Dimensions embedded |
| DQ-033 | What is the VMRS code for HOSE, A/C , COMPRESSOR TO CON? | 001-001-153 | _Testing_ | | Truncated at CON |
| DQ-036 | What is the VMRS code for COONECTOR KIT, EXPANSION VALVE? | 001-001-140 | _Testing_ | | Typo: COONECTOR |
| DQ-039 | What is the VMRS code for OUTLET LOUVER AIR COND GRY? | 001-001-221 | _Testing_ | | Color abbreviation GRY |

---

## Ambiguity Tests (10 samples)

Testing: Generic terms that should trigger clarification

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| AM-001 | What is the VMRS code for SEAL? | CLARIFIED | _Pending_ | | 304 parts, 106 VMRS codes |
| AM-002 | What is the VMRS code for SWITCH? | CLARIFIED | _Pending_ | | 280 parts, 90 VMRS codes |
| AM-004 | What is the VMRS code for HOSE? | CLARIFIED | _Pending_ | | 534 parts, 111 VMRS codes |
| AM-008 | What is the VMRS code for FILTER? | CLARIFIED | _Pending_ | | Air vs fuel vs oil |
| AM-009 | What is the VMRS code for RADIATOR? | CLARIFIED | _Pending_ | | 62 matches |
| AM-017 | What is the VMRS code for THERMOSTAT? | CLARIFIED | _Pending_ | | Cooling vs HVAC |
| AM-021 | What is the VMRS code for BATTERY? | 032-001-001 | _Pending_ | | 237 parts map here |
| AM-026 | What is the VMRS code for SEAL, OIL? | CLARIFIED | _Pending_ | | Oil seal in many systems |
| AM-027 | What is the VMRS code for HOSE, AIR? | CLARIFIED | _Pending_ | | Air hose multiple systems |
| AM-029 | What is the VMRS code for SENSOR, TEMPERATURE? | CLARIFIED | _Pending_ | | Temp sensors everywhere |

---

## Missing Data Tests (5 samples)

Testing: Known gaps and unclassified parts

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| MD-001 | What is the VMRS code for VENT, CAB EXHAUST? | 001-004-064 | _Pending_ | | Vendor-sourced component |
| MD-005 | What is the VMRS code for BATTERY, GROUP 51, 12V, 450CCA? | 032-001-001 | _Pending_ | | 237 vendor parts link here |
| MD-007 | What is the VMRS code for FRONT LINEAR ACTUATOR? | NOT_FOUND_OK | _Pending_ | | UNABLE TO CODE |
| MD-012 | What is the VMRS code for MOUNTING KIT? | NOT_FOUND_OK | _Pending_ | | Too generic |
| MD-015 | What is the VMRS code for SHIELD? | NOT_FOUND_OK | _Pending_ | | Too generic |

---

## Query Complexity Tests (10 samples)

Testing: Large results, hierarchy, comparisons

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| QC-001 | List all components in the Air Conditioning system | MULTIPLE | _Pending_ | | 754 vendor parts |
| QC-002 | What parts are in the Brakes system? | MULTIPLE | _Pending_ | | 2591 vendor parts |
| QC-006 | What vendor parts map to VMRS code 032-001-001? | MULTIPLE | _Pending_ | | 237 parts |
| QC-011 | What systems use SEAL parts? | MULTIPLE | _Pending_ | | 19 systems |
| QC-016 | What assembly does component 044-001-015 belong to? | 044-001 | _Pending_ | | Hierarchy up |
| QC-017 | What system contains assembly 013-010? | 013 | _Pending_ | | Hierarchy up |
| QC-018 | List all assemblies in the Fuel System (044) | MULTIPLE | _Pending_ | | Hierarchy down |
| QC-019 | What components are in assembly 001-001? | MULTIPLE | _Pending_ | | Hierarchy down |
| QC-020 | Show the hierarchy for VMRS code 013-017-007 | HIERARCHICAL | _Pending_ | | Full hierarchy |
| QC-021 | What is the difference between 001-001-062 and 001-001-065? | COMPARISON | _Pending_ | | Compare components |

---

## Natural Language Tests (10 samples)

Testing: Informal queries, typos, synonyms, case variations

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| NL-001 | whats the code for a brake pad | 013-017-003 | _Pending_ | | Informal style |
| NL-002 | gimme the vmrs for an ac compressor | 001-001-001 | _Pending_ | | Slang |
| NL-009 | What is the VMRS code for brakke pad? | 013-017-003 | _Pending_ | | Typo in brake |
| NL-011 | What is the VMRS code for altenator? | 032-003-001 | _Pending_ | | Typo in alternator |
| NL-016 | What is the VMRS code for AC compressor? | 001-001-001 | _Pending_ | | AC vs A/C |
| NL-018 | What is the VMRS code for windscreen? | 002-024-001 | _Pending_ | | British English |
| NL-019 | What is the VMRS code for bonnet? | 002-001-001 | _Pending_ | | British English |
| NL-024 | What is the VMRS code for BATTERY? | 032-001-001 | _Pending_ | | Uppercase |
| NL-025 | What is the VMRS code for battery? | 032-001-001 | _Pending_ | | Lowercase |
| NL-027 | What is the VMRS code for bAtTeRy? | 032-001-001 | _Pending_ | | Mixed case |

---

## Boundary Tests (5 samples)

Testing: Edge cases, malformed input, nonexistent parts

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| BD-001 | What is the VMRS code for S? | NOT_FOUND_OK | _Pending_ | | Single character |
| BD-006 | What is the VMRS code for BATTERY, GROUP 51, 12V, 450CCA, WET, MAINTENANCE FREE, HEAVY DUTY, COMMERCIAL VEHICLE, SIDE POST TERMINALS, 36 MONTH WARRANTY? | 032-001-001 | _Pending_ | | Very long description |
| BD-014 | What is the VMRS code for flux capacitor? | NOT_FOUND_OK | _Pending_ | | Fictional part |
| BD-019 | What is the VMRS code for 001-001? | 001-001-000 | _Pending_ | | Assembly code |
| BD-020 | What is the VMRS code for 001? | 001-000-000 | _Pending_ | | System code |

---

## Vendor Query Tests (10 samples)

Testing: "Who sells X?" queries

| ID | Question | Expected | Result | Actual Response | Notes |
|----|----------|----------|--------|-----------------|-------|
| VQ-001 | Which vendors sell batteries? | MULTIPLE | _Pending_ | | 35 vendors |
| VQ-002 | Who sells disc brake pads? | MULTIPLE | _Pending_ | | 32 vendors |
| VQ-003 | What vendors carry electrical connectors? | MULTIPLE | _Pending_ | | 31 vendors |
| VQ-007 | Which vendors carry air springs? | MULTIPLE | _Pending_ | | 27 vendors |
| VQ-012 | What vendors carry A/C condensers? | MULTIPLE | _Pending_ | | Multiple vendors |
| VQ-016 | Does Freightliner sell A/C condensers? | YES | _Pending_ | | Specific vendor query |
| VQ-020 | What A/C parts does Freightliner sell? | MULTIPLE | _Pending_ | | Vendor + system |
| VQ-023 | Which vendors have the most brake parts? | MULTIPLE | _Pending_ | | Ranking query |
| VQ-029 | who makes brake pads | MULTIPLE | _Pending_ | | Informal who sells |
| VQ-030 | where can i get a radiator | MULTIPLE | _Pending_ | | Informal availability |

---

## Summary Statistics

- **Total Tests Run:** 0/60
- **Pass Rate:** TBD
- **Tests by Category:**
  - Data Quality: 0/10
  - Ambiguity: 0/10
  - Missing Data: 0/5
  - Query Complexity: 0/10
  - Natural Language: 0/10
  - Boundary: 0/5
  - Vendor Query: 0/10

---

## Failure Modes Observed

_To be documented during testing_

---

## Recommendations

_To be added after testing_
