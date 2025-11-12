"""
Triple Extractor - LLM-based structured extraction for VMRS knowledge
"""

import json
import logging
from typing import Dict, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class TripleExtractor:
    """Extracts structured VMRS entities and relationships using Claude"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize extractor with Claude API
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: Claude Sonnet 4.5)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized TripleExtractor with model {model}")
    
    def extract_from_chunk(self, text: str, chunk_index: int = 0) -> Dict:
        """
        Extract VMRS entities and relationships from a text chunk
        
        Args:
            text: Text chunk to process
            chunk_index: Index of this chunk (for logging)
            
        Returns:
            Dictionary with extracted systems, assemblies, components, relationships
        """
        prompt = self._build_extraction_prompt(text)
        
        try:
            logger.info(f"Extracting from chunk {chunk_index}...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=16384,  # Increased to 16k to handle very large extraction outputs
                temperature=0,  # Deterministic extraction
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse JSON response
            content = response.content[0].text
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            logger.info(f"Chunk {chunk_index}: Extracted {len(result.get('systems', []))} systems, "
                       f"{len(result.get('assemblies', []))} assemblies, "
                       f"{len(result.get('components', []))} components")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from chunk {chunk_index}: {e}")
            logger.error(f"Response content (first 500 chars): {content[:500]}")
            
            # Try to salvage partial data from truncated JSON
            partial_result = self._try_salvage_partial_json(content, chunk_index)
            if partial_result:
                logger.warning(f"Salvaged partial data from chunk {chunk_index}: "
                             f"{len(partial_result.get('systems', []))} systems, "
                             f"{len(partial_result.get('assemblies', []))} assemblies, "
                             f"{len(partial_result.get('components', []))} components")
                return partial_result
            
            logger.error(f"Could not salvage data from chunk {chunk_index}, returning empty result")
            return self._empty_result()
        
        except Exception as e:
            logger.error(f"Error extracting from chunk {chunk_index}: {e}")
            return self._empty_result()
    
    def _build_extraction_prompt(self, text: str) -> str:
        """Build the extraction prompt for Claude"""
        return f"""You are extracting structured VMRS (Vehicle Maintenance Reporting Standards) data from technical documentation.

This is OCR-processed text with some cleanup. Tables may be partially malformed. Extract ALL valid systems, assemblies, and components.

**CODE FORMATS:**
- System codes: 3 digits (001-999, e.g., "044" or "013")
- Assembly codes: SYS-ASY format (e.g., "044-001" or "013-002")
- Component codes: SYS-ASY-COMP format (e.g., "044-001-015")

**WHERE TO FIND DATA:**
- Systems/Assemblies/Components: Look for "Code Key 31/32/33" sections
- Tables: Parse pipe-separated columns, first column is often the code
- Codes may appear as "013", "013-001", "013-001-015"
- Names are usually in adjacent table cells or after dashes/colons

**EXTRACTION RULES:**
1. Extract: code, name, description (if clearly available) for ALL entity types
2. For tables: Parse pipe-separated columns, first column is often the code
3. Ignore OCR artifacts: stray dots, dashes, or short repetitive strings
4. System codes: 001-999 (3 digits, numeric only)
5. Assembly codes: must have exactly 1 hyphen (XXX-XXX, numeric)
6. Component codes: must have exactly 2 hyphens (XXX-XXX-XXX, numeric)
7. If you see malformed codes, try to infer the valid code or skip
8. Skip if no clear name is associated with the code
9. DO NOT extract vendors - there are no vendor relationships in this file

**PARENT RELATIONSHIPS (auto-derived):**
- Assembly parent: first 3 digits before first hyphen
- Component parent: first 6 characters (XXX-XXX)

**OUTPUT FORMAT:**
Return ONLY valid JSON:

{{
  "systems": [
    {{"code": "044", "name": "Fuel System", "description": "..."}}
  ],
  "assemblies": [
    {{"code": "044-001", "name": "Fuel Tank", "parent_system_code": "044", "description": "..."}}
  ],
  "components": [
    {{"code": "044-001-015", "name": "Fuel Tank Cap", "parent_assembly_code": "044-001", "description": "..."}}
  ]
}}

Empty arrays if nothing found. Be generous but validate codes strictly.

**TEXT TO ANALYZE:**

{text}

**YOUR JSON RESPONSE:**"""
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            "systems": [],
            "assemblies": [],
            "components": []
        }
    
    def _try_salvage_partial_json(self, content: str, chunk_index: int) -> Dict:
        """
        Try to extract partial data from truncated JSON response.
        Uses regex to find complete JSON objects even if the overall JSON is malformed.
        
        Args:
            content: Truncated JSON content
            chunk_index: Chunk index for logging
            
        Returns:
            Dictionary with salvaged entities, or empty dict if nothing could be salvaged
        """
        import re
        
        salvaged = {
            "systems": [],
            "assemblies": [],
            "components": []
        }
        
        try:
            # Try to find complete JSON objects using regex
            # Pattern for system objects: {"code": "...", "name": "...", ...}
            system_pattern = r'\{"code"\s*:\s*"(\d{3})",\s*"name"\s*:\s*"([^"]*(?:\\.[^"]*)*)",\s*"description"\s*:\s*"([^"]*)"\}'
            assembly_pattern = r'\{"code"\s*:\s*"(\d{3}-\d{3})",\s*"name"\s*:\s*"([^"]*(?:\\.[^"]*)*)",\s*"parent_system_code"\s*:\s*"(\d{3})",\s*"description"\s*:\s*"([^"]*)"\}'
            component_pattern = r'\{"code"\s*:\s*"(\d{3}-\d{3}-\d{3})",\s*"name"\s*:\s*"([^"]*(?:\\.[^"]*)*)",\s*"parent_assembly_code"\s*:\s*"(\d{3}-\d{3})",\s*"description"\s*:\s*"([^"]*)"\}'
            
            # Extract systems
            for match in re.finditer(system_pattern, content):
                code, name, description = match.groups()
                if self._is_valid_system_code(code):
                    salvaged["systems"].append({
                        "code": code,
                        "name": name.replace('\\"', '"').replace('\\n', ' '),
                        "description": description.replace('\\"', '"').replace('\\n', ' ')
                    })
            
            # Extract assemblies
            for match in re.finditer(assembly_pattern, content):
                code, name, parent_code, description = match.groups()
                if self._is_valid_assembly_code(code):
                    salvaged["assemblies"].append({
                        "code": code,
                        "name": name.replace('\\"', '"').replace('\\n', ' '),
                        "parent_system_code": parent_code,
                        "description": description.replace('\\"', '"').replace('\\n', ' ')
                    })
            
            # Extract components
            for match in re.finditer(component_pattern, content):
                code, name, parent_code, description = match.groups()
                if self._is_valid_component_code(code):
                    salvaged["components"].append({
                        "code": code,
                        "name": name.replace('\\"', '"').replace('\\n', ' '),
                        "parent_assembly_code": parent_code,
                        "description": description.replace('\\"', '"').replace('\\n', ' ')
                    })
            
            # Return salvaged data if we found anything
            if salvaged["systems"] or salvaged["assemblies"] or salvaged["components"]:
                return salvaged
                
        except Exception as salvage_error:
            logger.error(f"Error during JSON salvage for chunk {chunk_index}: {salvage_error}")
        
        return {}
    
    def validate_extraction(self, result: Dict) -> Dict:
        """
        Validate and clean extracted data
        
        Args:
            result: Extraction result to validate
            
        Returns:
            Cleaned and validated result
        """
        validated = {
            "systems": [],
            "assemblies": [],
            "components": []
        }
        
        # Validate systems
        for system in result.get("systems", []):
            if self._is_valid_system_code(system.get("code", "")):
                validated["systems"].append({
                    "code": system["code"],
                    "name": system.get("name", ""),
                    "description": system.get("description", "")
                })
        
        # Validate assemblies
        for assembly in result.get("assemblies", []):
            if self._is_valid_assembly_code(assembly.get("code", "")):
                validated["assemblies"].append({
                    "code": assembly["code"],
                    "name": assembly.get("name", ""),
                    "parent_system_code": assembly["code"].split("-")[0],  # Auto-derive
                    "description": assembly.get("description", "")
                })
        
        # Validate components
        for component in result.get("components", []):
            if self._is_valid_component_code(component.get("code", "")):
                parts = component["code"].split("-")
                validated["components"].append({
                    "code": component["code"],
                    "name": component.get("name", ""),
                    "parent_assembly_code": f"{parts[0]}-{parts[1]}",  # Auto-derive
                    "description": component.get("description", "")
                })
        
        return validated
    
    def _is_valid_system_code(self, code: str) -> bool:
        """Check if system code is valid (XXX format, 001-999)"""
        if not code or "-" in code:
            return False
        try:
            num = int(code)
            return 1 <= num <= 999
        except ValueError:
            return False
    
    def _is_valid_assembly_code(self, code: str) -> bool:
        """Check if assembly code is valid (XXX-XXX format)"""
        if not code or code.count("-") != 1:
            return False
        try:
            parts = code.split("-")
            system = int(parts[0])
            assembly = int(parts[1])
            return 1 <= system <= 999 and 0 <= assembly <= 999
        except ValueError:
            return False
    
    def _is_valid_component_code(self, code: str) -> bool:
        """Check if component code is valid (XXX-XXX-XXX format)"""
        if not code or code.count("-") != 2:
            return False
        try:
            parts = code.split("-")
            system = int(parts[0])
            assembly = int(parts[1])
            component = int(parts[2])
            return 1 <= system <= 999 and 0 <= assembly <= 999 and 0 <= component <= 999
        except ValueError:
            return False
    

