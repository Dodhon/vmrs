# Issue: Vendor Count Discrepancy for Component 052-003-001

## Summary
The chatbot returns 9 vendors for component 052-003-001 (RADIO), but user expected only 6 unique vendors.

## Investigation Findings

### Database Query Result (9 vendors)
```
DUALE - DUAL ELECTRONICS CORPORATION
FORDX - FORD, A DIVISION OF FORD MOTOR CO.
FRGHT - FREIGHTLINER CORPORATION  
GMXXX - GENERAL MOTORS CORPORATION
NVSTR - NAVISTAR INTERNATIONAL TRANSPORTATION CORP.
PACCR - PACCAR CORPORATION
PIONR - PIONEER ELECTRONICS INC USA
PNPFC - PANA-PACIFIC (THE BRIX GROUP)
VLVNA - VOLVO TRUCKS NORTH AMERICA, INC.
```

### Source Data Analysis
The source file `vendor data/checked/Motors Part Cleanup - Return Data.csv` contains **31 records** for VMRS code 052-003-001 with **9 unique vendor codes**.

| Vendor Code | Vendor Name | Source Distributor | Example Part |
|-------------|-------------|-------------------|--------------|
| DUALE | DUAL ELECTRONICS CORPORATION | OREILLY AUTO PARTS | XRM47BT |
| FORDX | FORD, A DIVISION OF FORD MOTOR CO. | FORD MOTOR CO | CC2T-18K810-AA |
| FRGHT | FREIGHTLINER CORPORATION | FREIGHTLINER | A22-78677-000 |
| GMXXX | GENERAL MOTORS CORPORATION | GENERAL MOTORS CORP | 85586031 |
| NVSTR | NAVISTAR INTERNATIONAL TRANSPORTATION CORP. | INTERNATIONAL | 4154488C1 |
| PACCR | PACCAR CORPORATION | PETERBILT MOTORS CO | PP1071807001131100 |
| PIONR | PIONEER ELECTRONICS INC USA | PIONEER MFG, INC. | DH-S31BT |
| PNPFC | PANA-PACIFIC (THE BRIX GROUP) | PANA PACIFIC, VOLVO | PP107233 |
| VLVNA | VOLVO TRUCKS NORTH AMERICA, INC. | VOLVO | 24162031 |

### Root Cause
The database correctly reflects the source data. The discrepancy appears to be due to:
1. **User viewing a filtered subset** of the data (image shows ~10 rows with only 5 unique vendors)
2. The enrichment script `enrich_vmrs_with_vendor_data.py` aggregates **all unique vendor codes** from the source data

### Questions for Clarification
1. What criteria defines the "expected 6 vendors"? 
2. Should certain vendors be excluded based on:
   - Match score (e.g., only Match=1.0)?
   - Specific distributor relationships?
   - Data quality flags?

## Potential Solutions

### Option A: Filter by Match Score
Only include vendors with `Match = 1.0`:
```python
vendor_df = vendor_df[vendor_df['Match'] == 1.0]
```
Note: PIONR has one record with Match=0.0 (DH-S31BT)

### Option B: Define Vendor Inclusion Rules
Create business rules for which vendor relationships to include in the knowledge graph.

### Option C: Data Model Enhancement
Add relationship properties (e.g., `match_score`, `source`) to allow filtering at query time.

## Files Involved
- `scripts/enrich_vmrs_with_vendor_data.py` - Aggregation logic
- `scripts/create_vendor_nodes.py` - Vendor node creation
- `vendor data/checked/Motors Part Cleanup - Return Data.csv` - Source data

## Status
Needs clarification on expected vendor filtering criteria.

