"""
Generate constructed_code_9d for vendor parts using Neo4j and Claude Sonnet 4.5

For each vendor part description, queries Neo4j to find matching Systems,
Assemblies, and Components, then uses Claude to determine the best 9-digit code.
"""

import os
import csv
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jQueryClient:
    """Client for querying Neo4j to find matching VMRS codes"""
    
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def search_by_description(self, description: str, limit: int = 20) -> Dict:
        """
        Search for Systems, Assemblies, and Components matching the description
        
        Args:
            description: Vendor part description to search for
            limit: Maximum number of results per type
            
        Returns:
            Dictionary with systems, assemblies, and components lists
        """
        if not description or not description.strip():
            return {"systems": [], "assemblies": [], "components": []}
        
        # Clean description for search
        search_terms = description.strip()
        
        with self.driver.session() as session:
            # Query Systems
            systems_query = """
            MATCH (s:System)
            WHERE toLower(s.description) CONTAINS toLower($search) 
               OR toLower(s.name) CONTAINS toLower($search)
            RETURN s.code as code, s.name as name, s.description as description
            LIMIT $limit
            """
            systems = session.run(systems_query, search=search_terms, limit=limit).data()
            
            # Query Assemblies
            assemblies_query = """
            MATCH (a:Assembly)
            WHERE toLower(a.description) CONTAINS toLower($search) 
               OR toLower(a.name) CONTAINS toLower($search)
            RETURN a.code as code, a.name as name, a.description as description
            LIMIT $limit
            """
            assemblies = session.run(assemblies_query, search=search_terms, limit=limit).data()
            
            # Query Components
            components_query = """
            MATCH (c:Component)
            WHERE toLower(c.description) CONTAINS toLower($search) 
               OR toLower(c.name) CONTAINS toLower($search)
            RETURN c.code as code, c.name as name, c.description as description
            LIMIT $limit
            """
            components = session.run(components_query, search=search_terms, limit=limit).data()
            
            return {
                "systems": systems,
                "assemblies": assemblies,
                "components": components
            }


class CodeGenerator:
    """Uses Claude Sonnet 4.5 to generate constructed_code_9d from Neo4j matches"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize Claude client"""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized CodeGenerator with model {model}")
    
    def generate_code(
        self, 
        vendor_description: str,
        neo4j_matches: Dict
    ) -> Tuple[Optional[str], str]:
        """
        Generate constructed_code_9d and reasoning using Claude
        
        Args:
            vendor_description: Vendor part description
            neo4j_matches: Dictionary with systems, assemblies, components from Neo4j
            
        Returns:
            Tuple of (constructed_code_9d, reasoning)
        """
        prompt = self._build_prompt(vendor_description, neo4j_matches)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0,  # Deterministic
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            code = result.get("constructed_code_9d", "").strip()
            reasoning = result.get("reasoning", "").strip()
            
            # Validate code format (XXX-XXX-XXX)
            if code and not self._is_valid_9d_code(code):
                logger.warning(f"Invalid code format: {code}, setting to empty")
                code = ""
                reasoning = f"Invalid code format returned: {code}. {reasoning}"
            
            return (code if code else None, reasoning)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response content (first 500 chars): {content[:500]}")
            return (None, f"Error parsing LLM response: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return (None, f"Error: {str(e)}")
    
    def _build_prompt(self, vendor_description: str, neo4j_matches: Dict) -> str:
        """Build the prompt for Claude"""
        
        # Format Neo4j matches
        systems_text = "\n".join([
            f"  - Code: {s['code']}, Name: {s.get('name', 'N/A')}, Description: {s.get('description', 'N/A')[:100]}"
            for s in neo4j_matches.get("systems", [])[:10]
        ]) or "  (none found)"
        
        assemblies_text = "\n".join([
            f"  - Code: {a['code']}, Name: {a.get('name', 'N/A')}, Description: {a.get('description', 'N/A')[:100]}"
            for a in neo4j_matches.get("assemblies", [])[:10]
        ]) or "  (none found)"
        
        components_text = "\n".join([
            f"  - Code: {c['code']}, Name: {c.get('name', 'N/A')}, Description: {c.get('description', 'N/A')[:100]}"
            for c in neo4j_matches.get("components", [])[:10]
        ]) or "  (none found)"
        
        return f"""You are a VMRS (Vehicle Maintenance Reporting Standards) code matching expert.

**TASK:**
Given a vendor part description, determine the best matching 9-digit VMRS code (format: XXX-XXX-XXX) from the provided Neo4j database matches.

**VENDOR PART DESCRIPTION:**
{vendor_description}

**NEO4J DATABASE MATCHES:**

Systems (3-digit codes):
{systems_text}

Assemblies (6-digit codes, format: XXX-XXX):
{assemblies_text}

Components (9-digit codes, format: XXX-XXX-XXX):
{components_text}

**INSTRUCTIONS:**
1. Analyze the vendor part description carefully
2. Compare it against the Systems, Assemblies, and Components from Neo4j
3. Select the BEST matching 9-digit component code (XXX-XXX-XXX format)
4. If a component match is found, use that code
5. If only an assembly match is found, you may need to infer a component code (use 000 for the last segment if no specific component matches)
6. If only a system match is found, you may need to infer assembly and component codes (use 000 for missing segments)
7. If NO good match is found, return empty string for constructed_code_9d
8. Provide clear reasoning explaining your choice

**CODE FORMAT RULES:**
- Must be exactly XXX-XXX-XXX (three 3-digit numbers separated by hyphens)
- Each segment must be 000-999
- System code (first segment): typically 001-299
- Assembly code (second segment): typically 000-999
- Component code (third segment): typically 000-999

**OUTPUT FORMAT:**
Return ONLY valid JSON:
{{
  "constructed_code_9d": "044-001-015",
  "reasoning": "The vendor description 'Fuel Tank Cap' matches Component code 044-001-015 (Fuel Tank Cap) in the database. This is a direct match with high confidence."
}}

If no match found:
{{
  "constructed_code_9d": "",
  "reasoning": "No matching VMRS codes found in the database for this description. The description does not clearly match any Systems, Assemblies, or Components."
}}

**YOUR JSON RESPONSE:**"""
    
    def _is_valid_9d_code(self, code: str) -> bool:
        """Validate 9-digit code format (XXX-XXX-XXX)"""
        if not code:
            return False
        parts = code.split("-")
        if len(parts) != 3:
            return False
        try:
            for part in parts:
                num = int(part)
                if not (0 <= num <= 999):
                    return False
            return True
        except ValueError:
            return False


class ConstructedCodeProcessor:
    """Main processor for generating constructed codes"""
    
    def __init__(
        self,
        csv_path: str,
        neo4j_uri: str,
        neo4j_username: str,
        neo4j_password: str,
        anthropic_api_key: str
    ):
        """Initialize processor"""
        self.csv_path = csv_path
        self.neo4j_client = Neo4jQueryClient(neo4j_uri, neo4j_username, neo4j_password)
        self.code_generator = CodeGenerator(anthropic_api_key)
        
        # Rate limiting: Anthropic allows 50 RPM, so wait 1.2 seconds between requests
        self.anthropic_delay = 1.2  # seconds between Anthropic API calls
        self.neo4j_delay = 0.1  # seconds between Neo4j queries (minimal delay)
        
        # Progress tracking
        self.processed_count = 0
        self.save_interval = 100  # Save every 100 rows
    
    def process_all(self):
        """Process all rows in the CSV"""
        logger.info(f"Starting processing of {self.csv_path}")
        
        # Read all rows
        rows = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        total_rows = len(rows)
        logger.info(f"Total rows to process: {total_rows}")
        
        # Process each row
        for idx, row in enumerate(rows, 1):
            # Skip if already has constructed_code_9d
            if row.get('constructed_code_9d', '').strip():
                logger.debug(f"Row {idx}: Skipping (already has code)")
                continue
            
            description = row.get('DESCRIPTION', '').strip()
            if not description:
                logger.debug(f"Row {idx}: Skipping (no description)")
                continue
            
            try:
                # Query Neo4j
                logger.info(f"Row {idx}/{total_rows}: Querying Neo4j for '{description[:50]}...'")
                time.sleep(self.neo4j_delay)
                neo4j_matches = self.neo4j_client.search_by_description(description)
                
                # Generate code with Claude
                logger.info(f"Row {idx}/{total_rows}: Generating code with Claude...")
                time.sleep(self.anthropic_delay)
                code, reasoning = self.code_generator.generate_code(description, neo4j_matches)
                
                # Update row
                row['constructed_code_9d'] = code or ''
                row['reasoning'] = reasoning
                
                self.processed_count += 1
                
                logger.info(f"Row {idx}/{total_rows}: Generated code '{code}'")
                
                # Save progress periodically
                if self.processed_count % self.save_interval == 0:
                    self._save_csv(rows)
                    logger.info(f"Progress saved: {self.processed_count} rows processed")
                
            except Exception as e:
                logger.error(f"Row {idx}: Error processing - {e}")
                row['reasoning'] = f"Error: {str(e)}"
                continue
        
        # Final save
        self._save_csv(rows)
        logger.info(f"Processing complete! Processed {self.processed_count} rows")
    
    def _save_csv(self, rows: List[Dict]):
        """Save rows to CSV"""
        if not rows:
            return
        
        fieldnames = rows[0].keys()
        
        # Write to temporary file first, then replace
        temp_path = self.csv_path + '.tmp'
        with open(temp_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        # Replace original file
        os.replace(temp_path, self.csv_path)
        logger.debug(f"CSV saved to {self.csv_path}")
    
    def close(self):
        """Close connections"""
        self.neo4j_client.close()


def main():
    """Main entry point"""
    # Load configuration from environment
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Get absolute path to CSV (works from any directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    csv_path = os.path.join(project_root, "llm_matching", "vendor_parts_constructed_code_9d.csv")
    
    # Validate configuration
    if not neo4j_password:
        logger.error("Please set NEO4J_PASSWORD in .env file")
        return
    
    if not anthropic_api_key:
        logger.error("Please set ANTHROPIC_API_KEY in .env file")
        return
    
    # Initialize processor
    processor = ConstructedCodeProcessor(
        csv_path=csv_path,
        neo4j_uri=neo4j_uri,
        neo4j_username=neo4j_username,
        neo4j_password=neo4j_password,
        anthropic_api_key=anthropic_api_key
    )
    
    try:
        processor.process_all()
    finally:
        processor.close()


if __name__ == "__main__":
    main()

