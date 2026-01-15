"""!
@file main.py
@brief The Main Entry Point for the CareerNavigator DataFactory Pipeline.
"""

from typing import List, Dict, Tuple, Any
from collections import Counter

# Internal Modules
from config import cfg
from ingestion.reader import Reader
from ingestion.writer import Writer
from core.taxonomy import TaxonomyManager
from core.graph_engine import GraphBuilder, GraphStats
from utils.text_processor import TextProcessor
from utils.seniority_analyzer import SeniorityAnalyzer
from utils.analytics import AnalyticsEngine
from utils.logger import get_logger

# Initialize Logger
logger = get_logger(__name__)

def analyze_jd_content(
    jd_text: str,
    matchable_terms: List[str],
    alias_map: Dict[str, str]) -> Tuple[List[str], bool, str]:
    """!
    @brief Analyzes a single Job Description to extract skills and determine seniority.
    """
    # 1. Detect Seniority
    title: str = TextProcessor.extract_title_candidate(jd_text)
    seniority_info: Dict[str, Any] = SeniorityAnalyzer.detect_seniority(title, jd_text)
    
    # 2. Extract Skills (Using Greedy Longest-Match Strategy)
    found_skills: List[str] = TextProcessor.extract_skills(jd_text, matchable_terms, alias_map)
    
    return found_skills, seniority_info['is_senior'], seniority_info['level']

def print_execution_summary(jds_count: int, nodes_count: int, edges_count: int, seniority_dist: Counter) -> None:
    logger.info(f"✨ Done! Processed {jds_count} JDs.")
    logger.info(f"Found {nodes_count} filtered skills and {edges_count} filtered edges")
    logger.info("📊 Seniority Distribution:")
    for level, count in seniority_dist.items():
        logger.info(f"  - {level}: {count}")


def init_data() -> Tuple[List[str], GraphStats, List[str], Dict[str, str], Dict[str, str], int]:
    """!
    @brief Initializes the data processing pipeline.
    """
    # Load Config
    # Config is autoloaded on import of cfg
    threshold = cfg.get("pipeline.threshold", 1) #check the count of nodes before taking it seriously, set to 1 by default
    input_path = cfg.get_abs_path("paths.test_input")

    # 1. ---- Load Data
    logger.info(f"Scanning raw data from {input_path}...")
    jds: List[str] = Reader.load_raw_jds(file_path=input_path)
    if not jds:
        logger.warning("No Job Descriptions found.")
        return [], GraphBuilder.initialize_stats([]), [], {}, {}, threshold
    logger.info(f"📖 Found {len(jds)} Job Descriptions. Analyzing...")

    # 2. ---- Initialize Taxonomy & Stats
    logger.info("Loading Taxonomy...")
    all_skills = TaxonomyManager.get_all_skills()
    matchable_terms = TaxonomyManager.get_matchable_terms()
    alias_map = TaxonomyManager.get_alias_map()
    skill_to_group = TaxonomyManager.get_skill_to_group_map()

    logger.info(f"Taxonomy loaded: {len(all_skills)} canonical skills, {len(matchable_terms)} matchable terms, {len(alias_map)} alias mappings.")

    stats = GraphBuilder.initialize_stats(all_skills)
    logger.info("Graph statistics initialized.")
    
    return jds, stats, matchable_terms, alias_map, skill_to_group, threshold

def process_data() -> None:
    """!
    @brief The main orchestrator function.
    """
    logger.info("🚀 Starting Data Factory...")

    jds, stats, matchable_terms, alias_map, skill_to_group, threshold = init_data()
    
    if not jds:
        logger.error("No JDs found. Exiting.")
        return

    # 3. ---- Main Processing Loop
    logger.info("Starting analysis of Job Descriptions...")
    total_jds = len(jds)
    
    for idx, jd in enumerate(jds):
        found_skills, is_senior, level = analyze_jd_content(jd, matchable_terms, alias_map)
        
        stats.seniority_dist[level] += 1
        GraphBuilder.update_metrics(stats, found_skills, level)
        
        # Log progress every 100 JDs
        if (idx + 1) % 100 == 0:
            logger.info(f"Processed {idx + 1}/{total_jds} JDs...")

    logger.info("JD Analysis complete.")

    # 4. Final Transformation
    logger.info("Performing final graph transformations and filtering...")
    final_nodes_list, active_node_ids, seniority_scores = GraphBuilder.prepare_nodes_list(stats.node_stats, skill_to_group, threshold)
    logger.info(f"Nodes prepared: {len(final_nodes_list)} active nodes (Threshold: {threshold}).")
    
    filtered_edge_counts = GraphBuilder.filter_edges(stats.edge_counts, active_node_ids, threshold)
    logger.info(f"Edges filtered: {len(filtered_edge_counts)} edges remaining.")
    
    meta = AnalyticsEngine.calculate_seniority_distribution(seniority_scores, len(final_nodes_list))
    logger.info("Seniority distribution calculated.")

    # 5. Export
    output_dir = cfg.get_abs_path("paths.output_dir")
    logger.info(f"Exporting data to {output_dir}...")
    Writer.save_universe(final_nodes_list, filtered_edge_counts, meta=meta, output_dir=output_dir)
    
    # 6. Cosmograph Export
    logger.info("Exporting Cosmograph files...")
    filtered_node_stats = {k: v for k, v in stats.node_stats.items() if k in active_node_ids}
    Writer.save_cosmograph_files(filtered_node_stats, filtered_edge_counts, skill_to_group, output_dir=output_dir)

    # 7. Summary
    print_execution_summary(len(jds), len(final_nodes_list), len(filtered_edge_counts), stats.seniority_dist)

if __name__ == "__main__":
    process_data()