"""
Manual Graph Builder - Orchestrates the extraction pipeline
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .text_chunker import TextChunker
from .triple_extractor import TripleExtractor
from .neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ManualGraphBuilder:
    """Orchestrates extraction and graph building from VMRS manuals"""
    
    def __init__(self, anthropic_api_key: str, neo4j_uri: Optional[str] = None,
                 neo4j_username: Optional[str] = None, neo4j_password: Optional[str] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize the graph builder
        
        Args:
            anthropic_api_key: Anthropic API key for Claude
            neo4j_uri: Neo4j connection URI (optional, for graph storage)
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
            output_dir: Optional custom output directory. If None, creates unique folder per run
        """
        self.chunker = TextChunker(chunk_size=2000, overlap=200)  # Reduced to prevent truncation
        self.extractor = TripleExtractor(api_key=anthropic_api_key)
        
        # Initialize Neo4j client if credentials provided
        self.neo4j_client = None
        if neo4j_uri and neo4j_username and neo4j_password:
            self.neo4j_client = Neo4jClient(neo4j_uri, neo4j_username, neo4j_password)
            self.neo4j_client.create_indexes()
            logger.info("Neo4j client initialized")
        else:
            logger.info("Running without Neo4j (JSON export only)")
        
        # Set up output directory - create unique folder per run
        base_output_dir = Path("knowledge_graph_output")
        base_output_dir.mkdir(exist_ok=True)
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Create unique folder with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = base_output_dir / f"run_{timestamp}"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
        
        # Track statistics
        self.stats = {
            "total_chunks": 0,
            "total_systems": 0,
            "total_assemblies": 0,
            "total_components": 0,
            "total_relationships": 0
        }
        
        # Store all extracted data
        self.all_entities = {
            "systems": {},      # code -> entity
            "assemblies": {},   # code -> entity
            "components": {}    # code -> entity
        }
    
    def build_graph_from_manual(self, file_path: str, start_chunk: int = 0,
                                process_temporal_schema: bool = False,
                                save_every: int = 1) -> Dict:
        """
        Build knowledge graph from a manual file
        
        Args:
            file_path: Path to the text file to process
            start_chunk: Starting chunk index (for resuming)
            process_temporal_schema: Whether to process temporal patterns (not implemented yet)
            save_every: Save progress every N chunks
            
        Returns:
            Dictionary with statistics and extracted data
        """
        logger.info(f"Building graph from {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"Read {len(text)} characters from file")
        
        # Chunk the text
        chunks = self.chunker.chunk_text(text)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            if i < start_chunk:
                logger.info(f"Skipping chunk {i} (before start_chunk)")
                continue
            
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            
            # Extract entities and relationships
            result = self.extractor.extract_from_chunk(chunk['text'], chunk_index=i)
            
            # Validate extraction
            validated = self.extractor.validate_extraction(result)
            
            # Merge into all_entities (deduplication)
            self._merge_entities(validated)
            
            # Save to Neo4j if available
            if self.neo4j_client:
                self._save_to_neo4j(validated)
            
            # Save progress periodically
            if (i + 1) % save_every == 0:
                self._save_progress(file_path, i + 1)
            
            self.stats["total_chunks"] = i + 1
        
        # Final statistics
        self.stats["total_systems"] = len(self.all_entities["systems"])
        self.stats["total_assemblies"] = len(self.all_entities["assemblies"])
        self.stats["total_components"] = len(self.all_entities["components"])
        
        # Get Neo4j stats if available and fix any missing relationships
        if self.neo4j_client:
            # Fix missing relationships (in case parents were created after children)
            logger.info("Fixing missing relationships...")
            self.neo4j_client.fix_missing_relationships()
            neo4j_stats = self.neo4j_client.get_statistics()
            self.stats["total_relationships"] = neo4j_stats["total_relationships"]
        else:
            # Calculate relationships from entity data when not using Neo4j
            # Each assembly with a parent_system_code = 1 relationship (Assembly -> System)
            # Each component with a parent_assembly_code = 1 relationship (Component -> Assembly)
            assembly_relationships = sum(
                1 for assembly in self.all_entities["assemblies"].values()
                if assembly.get("parent_system_code")
            )
            component_relationships = sum(
                1 for component in self.all_entities["components"].values()
                if component.get("parent_assembly_code")
            )
            self.stats["total_relationships"] = assembly_relationships + component_relationships
            logger.info(f"Calculated {assembly_relationships} assembly->system relationships and "
                       f"{component_relationships} component->assembly relationships")
        
        logger.info(f"Extraction complete! {self.stats}")
        
        return {
            "total_chunks": self.stats["total_chunks"],
            "total_eec_documents": self.stats["total_chunks"],  # For compatibility
            "total_entities": self.stats["total_systems"] + self.stats["total_assemblies"] + self.stats["total_components"],
            "total_systems": self.stats["total_systems"],
            "total_assemblies": self.stats["total_assemblies"],
            "total_components": self.stats["total_components"],
            "total_events": 0,  # Not used in structured extraction
            "total_concepts": 0,  # Not used in structured extraction
            "total_relationships": self.stats["total_relationships"],
            "eec_documents": [self.all_entities],  # For compatibility
            "temporal_patterns": None,
            "schemas": None
        }
    
    def _merge_entities(self, validated: Dict):
        """Merge newly extracted entities into all_entities (deduplication)"""
        for system in validated["systems"]:
            code = system["code"]
            if code not in self.all_entities["systems"]:
                self.all_entities["systems"][code] = system
            else:
                # Update with longer description if available
                if len(system.get("description", "")) > len(self.all_entities["systems"][code].get("description", "")):
                    self.all_entities["systems"][code] = system
        
        for assembly in validated["assemblies"]:
            code = assembly["code"]
            if code not in self.all_entities["assemblies"]:
                self.all_entities["assemblies"][code] = assembly
            else:
                if len(assembly.get("description", "")) > len(self.all_entities["assemblies"][code].get("description", "")):
                    self.all_entities["assemblies"][code] = assembly
        
        for component in validated["components"]:
            code = component["code"]
            if code not in self.all_entities["components"]:
                self.all_entities["components"][code] = component
            else:
                if len(component.get("description", "")) > len(self.all_entities["components"][code].get("description", "")):
                    self.all_entities["components"][code] = component
    
    def _save_to_neo4j(self, validated: Dict):
        """Save validated entities to Neo4j"""
        if not self.neo4j_client:
            return
        
        # Create systems
        for system in validated["systems"]:
            self.neo4j_client.create_system(
                code=system["code"],
                name=system["name"],
                description=system.get("description", "")
            )
        
        # Create assemblies (will auto-link to parent systems)
        for assembly in validated["assemblies"]:
            self.neo4j_client.create_assembly(
                code=assembly["code"],
                name=assembly["name"],
                parent_system_code=assembly["parent_system_code"],
                description=assembly.get("description", "")
            )
        
        # Create components (will auto-link to parent assemblies)
        for component in validated["components"]:
            self.neo4j_client.create_component(
                code=component["code"],
                name=component["name"],
                parent_assembly_code=component["parent_assembly_code"],
                description=component.get("description", "")
            )
    
    def _save_progress(self, file_path: str, chunk_num: int):
        """Save progress to JSON file"""
        progress_file = self.output_dir / f"progress_chunk_{chunk_num}.json"
        
        progress_data = {
            "file_path": file_path,
            "chunk_number": chunk_num,
            "statistics": self.stats,
            "entities_count": {
                "systems": len(self.all_entities["systems"]),
                "assemblies": len(self.all_entities["assemblies"]),
                "components": len(self.all_entities["components"])
            }
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        logger.info(f"Progress saved to {progress_file}")
    
    def export_eec_json(self, eec_documents: List, output_filename: str = "knowledge_graph.json"):
        """
        Export extracted entities to JSON file
        
        Args:
            eec_documents: List of entity documents (or dict with all entities)
            output_filename: Output filename (will be saved in the run's output directory)
                           If default "knowledge_graph.json", timestamp will be added automatically
        """
        # Add timestamp to filename if using default name
        if output_filename == "knowledge_graph.json":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"knowledge_graph_{timestamp}.json"
        
        output_path = self.output_dir / output_filename
        
        # Convert to list format if needed
        if isinstance(eec_documents, list) and len(eec_documents) > 0:
            data = eec_documents[0] if isinstance(eec_documents[0], dict) else {}
        else:
            data = self.all_entities
        
        # Format for export
        extraction_timestamp = datetime.now().isoformat()
        export_data = {
            "metadata": {
                "total_systems": len(data.get("systems", {})),
                "total_assemblies": len(data.get("assemblies", {})),
                "total_components": len(data.get("components", {})),
                "extraction_date": extraction_timestamp
            },
            "systems": list(data.get("systems", {}).values()),
            "assemblies": list(data.get("assemblies", {}).values()),
            "components": list(data.get("components", {}).values())
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {export_data['metadata']['total_systems']} systems, "
                   f"{export_data['metadata']['total_assemblies']} assemblies, "
                   f"{export_data['metadata']['total_components']} components to {output_path}")
    
    @staticmethod
    def archive_existing_outputs():
        """
        Archive all existing files in knowledge_graph_output into a timestamped folder.
        This should be called before starting a new extraction run.
        """
        base_output_dir = Path("knowledge_graph_output")
        if not base_output_dir.exists():
            logger.info("Output directory doesn't exist, nothing to archive")
            return
        
        # Get all files (not directories) in the output directory
        existing_files = [f for f in base_output_dir.iterdir() if f.is_file()]
        
        if not existing_files:
            logger.info("No existing files to archive")
            return
        
        # Create archive folder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = base_output_dir / f"archive_{timestamp}"
        archive_dir.mkdir(exist_ok=True)
        
        # Move all files to archive folder
        moved_count = 0
        for file in existing_files:
            try:
                shutil.move(str(file), str(archive_dir / file.name))
                moved_count += 1
            except Exception as e:
                logger.warning(f"Failed to move {file.name}: {e}")
        
        logger.info(f"Archived {moved_count} files to {archive_dir}")
        return archive_dir
    
    def close(self):
        """Clean up resources"""
        if self.neo4j_client:
            self.neo4j_client.close()
            logger.info("Graph builder closed")

