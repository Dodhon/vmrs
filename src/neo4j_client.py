"""
Neo4j Client - Interface for graph database operations
"""

from typing import Dict, List, Optional
from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Client for Neo4j graph database operations"""
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            username: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def create_indexes(self):
        """Create indexes for performance"""
        with self.driver.session() as session:
            # Index on System code
            session.run("""
                CREATE INDEX system_code_idx IF NOT EXISTS 
                FOR (s:System) ON (s.code)
            """)
            
            # Index on Assembly code
            session.run("""
                CREATE INDEX assembly_code_idx IF NOT EXISTS 
                FOR (a:Assembly) ON (a.code)
            """)
            
            # Index on Component code
            session.run("""
                CREATE INDEX component_code_idx IF NOT EXISTS 
                FOR (c:Component) ON (c.code)
            """)
            
            # Index on Vendor code
            session.run("""
                CREATE INDEX vendor_code_idx IF NOT EXISTS 
                FOR (v:Vendor) ON (v.code)
            """)
            
            logger.info("Created indexes")
    
    def create_system(self, code: str, name: str, description: str = "") -> Dict:
        """
        Create or merge a System node
        
        Args:
            code: System code (e.g., "044")
            name: System name (e.g., "Fuel System")
            description: Optional description
            
        Returns:
            Created/merged node properties
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (s:System {code: $code})
                SET s.name = $name,
                    s.description = $description,
                    s.updated_at = timestamp()
                RETURN s
            """, code=code, name=name, description=description)
            
            record = result.single()
            return dict(record["s"]) if record else {}
    
    def create_assembly(self, code: str, name: str, parent_system_code: str, 
                       description: str = "") -> Dict:
        """
        Create or merge an Assembly node and link to parent System
        
        Args:
            code: Assembly code (e.g., "044-001")
            name: Assembly name
            parent_system_code: Parent system code (e.g., "044")
            description: Optional description
            
        Returns:
            Created/merged node properties
        """
        with self.driver.session() as session:
            # Create assembly node first
            session.run("""
                MERGE (a:Assembly {code: $code})
                SET a.name = $name,
                    a.description = $description,
                    a.updated_at = timestamp()
            """, code=code, name=name, description=description)
            
            # Check if parent system exists and create relationship
            check_system = session.run("""
                MATCH (s:System {code: $parent_code})
                RETURN s
            """, parent_code=parent_system_code).single()
            
            if check_system:
                # System exists, create relationship
                session.run("""
                    MATCH (a:Assembly {code: $code}), (s:System {code: $parent_code})
                    MERGE (a)-[:PART_OF]->(s)
                """, code=code, parent_code=parent_system_code)
            else:
                logger.warning(f"Assembly {code} created but parent system {parent_system_code} not found - relationship will be created when system is added")
            
            # Return the assembly
            result = session.run("MATCH (a:Assembly {code: $code}) RETURN a", code=code)
            record = result.single()
            return dict(record["a"]) if record else {}
    
    def create_component(self, code: str, name: str, parent_assembly_code: str,
                        description: str = "") -> Dict:
        """
        Create or merge a Component node and link to parent Assembly
        
        Args:
            code: Component code (e.g., "044-001-015")
            name: Component name
            parent_assembly_code: Parent assembly code (e.g., "044-001")
            description: Optional description
            
        Returns:
            Created/merged node properties
        """
        with self.driver.session() as session:
            # Create component node
            session.run("""
                MERGE (c:Component {code: $code})
                SET c.name = $name,
                    c.description = $description,
                    c.updated_at = timestamp()
            """, code=code, name=name, description=description)
            
            # Check if parent assembly exists and create relationship
            check_assembly = session.run("""
                MATCH (a:Assembly {code: $parent_code})
                RETURN a
            """, parent_code=parent_assembly_code).single()
            
            if check_assembly:
                # Assembly exists, create relationship
                session.run("""
                    MATCH (c:Component {code: $code}), (a:Assembly {code: $parent_code})
                    MERGE (c)-[:PART_OF]->(a)
                """, code=code, parent_code=parent_assembly_code)
            else:
                logger.warning(f"Component {code} created but parent assembly {parent_assembly_code} not found - relationship not created")
            
            # Return the component
            result = session.run("MATCH (c:Component {code: $code}) RETURN c", code=code)
            record = result.single()
            return dict(record["c"]) if record else {}
    
    def create_vendor(self, code: str, name: str, description: str = "") -> Dict:
        """
        Create or merge a Vendor node
        
        Args:
            code: Vendor code (e.g., "CHVRL")
            name: Vendor/Manufacturer name (e.g., "Chevrolet Motor Div. of General Motors Corp.")
            description: Optional description
            
        Returns:
            Created/merged node properties
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (v:Vendor {code: $code})
                SET v.name = $name,
                    v.description = $description,
                    v.updated_at = timestamp()
                RETURN v
            """, code=code, name=name, description=description)
            
            record = result.single()
            return dict(record["v"]) if record else {}
    
    def fix_missing_relationships(self):
        """
        Fix missing relationships for assemblies and components.
        This should be called after all nodes are imported to ensure
        relationships are created even if parent nodes were created later.
        """
        with self.driver.session() as session:
            # Fix Assembly -> System relationships
            # Extract system code from assembly code (first part: "044" from "044-001")
            result = session.run("""
                MATCH (a:Assembly)
                WHERE NOT (a)-[:PART_OF]->()
                WITH a, split(a.code, '-') as parts
                WHERE size(parts) >= 1
                WITH a, parts[0] as system_code
                MATCH (s:System {code: system_code})
                MERGE (a)-[:PART_OF]->(s)
                RETURN count(*) as fixed
            """)
            record = result.single()
            fixed_assemblies = record["fixed"] if record else 0
            
            # Fix Component -> Assembly relationships
            # Extract assembly code from component code (first two parts: "044-001" from "044-001-015")
            result = session.run("""
                MATCH (c:Component)
                WHERE NOT (c)-[:PART_OF]->()
                WITH c, split(c.code, '-') as parts
                WHERE size(parts) >= 2
                WITH c, parts[0] + '-' + parts[1] as assembly_code
                MATCH (a:Assembly {code: assembly_code})
                MERGE (c)-[:PART_OF]->(a)
                RETURN count(*) as fixed
            """)
            record = result.single()
            fixed_components = record["fixed"] if record else 0
            
            if fixed_assemblies > 0 or fixed_components > 0:
                logger.info(f"Fixed {fixed_assemblies} assembly relationships and {fixed_components} component relationships")
            else:
                logger.info("All relationships are already created")
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get graph statistics
        
        Returns:
            Dictionary with node and relationship counts
        """
        with self.driver.session() as session:
            # Count nodes
            systems = session.run("MATCH (s:System) RETURN count(s) as count").single()["count"]
            assemblies = session.run("MATCH (a:Assembly) RETURN count(a) as count").single()["count"]
            components = session.run("MATCH (c:Component) RETURN count(c) as count").single()["count"]
            vendors = session.run("MATCH (v:Vendor) RETURN count(v) as count").single()["count"]
            
            # Count relationships
            part_of = session.run("MATCH ()-[r:PART_OF]->() RETURN count(r) as count").single()["count"]
            
            return {
                "systems": systems,
                "assemblies": assemblies,
                "components": components,
                "vendors": vendors,
                "part_of_relationships": part_of,
                "total_nodes": systems + assemblies + components + vendors,
                "total_relationships": part_of
            }
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.warning("Database cleared!")



