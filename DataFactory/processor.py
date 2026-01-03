"""!
@file processor.py
@brief The Main Entry Point for the CareerNavigator DataFactory Pipeline.

@details
This script orchestrates the entire process of transforming raw job descriptions into a structured skill graph (Universe).
It follows a linear pipeline:
1.  <b>Load Data</b>: Reads raw text data from disk via `IOHandler`.
2.  <b>Initialize Stats</b>: Sets up the graph topology using `GraphBuilder` and `TaxonomyManager`.
3.  <b>Process Loop</b>: Iterates through every JD, delegating analysis to:
    -   `TextProcessor` for extracting skills and seniority.
    -   `GraphBuilder` for updating statistical counters (nodes and edges).
4.  <b>Transformation</b>: Converts raw counters into statistical probabilities (e.g., conditional probabilities for edges).
5.  <b>Export</b>: Saves the resulting 'Universe' to JSON and CSV formats for visualization.

@author CareerNavigator Team
@version 1.0.0
"""

from typing import List, Dict, Tuple, Any
from collections import Counter
from utils.text_processor import TextProcessor
from utils.io_handler import IOHandler
from utils.taxonomy_manager import TaxonomyManager
from utils.graph_builder import GraphBuilder
from utils.analytics_engine import AnalyticsEngine

# --- Global Constants (Configuration) ---
## @brief Metadata: Valid skills loaded from the taxonomy.
ALL_SKILLS: List[str] = TaxonomyManager.get_all_skills()

## @brief Metadata: Mapping of skills to their categories (e.g., "Python" -> "Languages").
SKILL_TO_GROUP: Dict[str, str] = TaxonomyManager.get_skill_to_group_map()

## @brief Config: Minimum occurrences required for a node/edge to be included in the final graph.
THRESHOLD: int = 1

# --- Core Logic Step 1: Analyze Single JD ---
def analyze_jd_content(jd_text: str) -> Tuple[List[str], bool, str]:
    """!
    @brief Analyzes a single Job Description to extract skills and determine seniority.
    
    @details
    Delegates deeper NLP tasks to `TextProcessor`.
    
    @param jd_text The raw text of the job description.
    @return A tuple containing:
        - `found_skills` (List[str]): List of valid skills found in the text.
        - `is_senior` (bool): True if the role is Senior/Managerial.
        - `level` (str): Specific level classification ('Junior', 'Mid', 'Senior', 'Managerial').
    """
    # 1. Detect Seniority
    lines: List[str] = jd_text.split('\n')
    title: str = lines[0] if lines else ""
    seniority_info: Dict[str, Any] = TextProcessor.detect_seniority(title, jd_text)
    
    # 2. Extract Skills
    found_skills: List[str] = TextProcessor.extract_skills(jd_text, ALL_SKILLS)
    
    return found_skills, seniority_info['is_senior'], seniority_info['level']

# --- Reporting ---
def print_execution_summary(
    jds_count: int, 
    nodes_count: int, 
    edges_count: int, 
    seniority_dist: Counter
) -> None:
    """!
    @brief Prints a human-readable summary of the pipeline execution to the console.
    
    @param jds_count Total number of JDs processed.
    @param nodes_count Number of unique skills (nodes) remaining after filtering.
    @param edges_count Number of skill relationships (edges) remaining after filtering.
    @param seniority_dist A Counter object with the breakdown of roles by seniority level.
    """
    print(f"\n✨ Done! Processed {jds_count} JDs.")
    print(f"Found {nodes_count} filtered skills (Threshold: {THRESHOLD}) and {edges_count} filtered edges")
    print("📊 Seniority Distribution:")
    for level, count in seniority_dist.items():
        print(f"  - {level}: {count}")

# --- Orchestrator ---
def process_data() -> None:
    """!
    @brief The main orchestrator function.
    
    @details
    EXECUTION FLOW:
    1.  **Load Raw Data**: Checks for `raw_jds.txt`. Uses a backup file if in debug mode.
    2.  **Initialize**: Creation of zero-initialized statistical containers.
    3.  **Processing Loop**:
        -   Parses every JD.
        -   Accumulates metrics in `node_stats` and `edge_counts`.
    4.  **Finalization**:
        -   Computes seniority scores from raw counts.
        -   Filters low-frequency noise (Thresholding).
        -   Calculates global analytics (e.g. seniority distribution).
    5.  **Output**: Writes `universe.json` (for Core usage) and CSVs (for Cosmograph).
    """
    print("🚀 Starting Data Factory...")

    debug: bool = False
    # 1. Load Data
    jds: List[str] = IOHandler.load_raw_jds() if debug == False else IOHandler.load_raw_jds(file_path="raw_jds copy.txt")
    if not jds:
        return
    print(f"📖 Found {len(jds)} Job Descriptions. Analyzing...")

    # 2. Initialize
    node_stats, edge_counts, seniority_dist = GraphBuilder.initialize_stats(ALL_SKILLS)

    # 3. Main Processing Loop
    for jd in jds:
        found_skills, is_senior, level = analyze_jd_content(jd)
        
        seniority_dist[level] += 1
        GraphBuilder.update_metrics(node_stats, edge_counts, found_skills, level)

    # 4. Final Transformation
    final_nodes_list, active_node_ids, seniority_scores = GraphBuilder.prepare_nodes_list(node_stats, SKILL_TO_GROUP, THRESHOLD)
    filtered_edge_counts = GraphBuilder.filter_edges(edge_counts, active_node_ids, THRESHOLD)
    meta = AnalyticsEngine.calculate_seniority_distribution(seniority_scores, len(final_nodes_list))

    # 5. Export
    IOHandler.save_universe(final_nodes_list, filtered_edge_counts, meta=meta)
    
    # For cosmograph, we can pass the filtered sets or full. 
    # Usually cosmograph is for exploration, let's keep consistent with filtering.
    filtered_node_stats = {k: v for k, v in node_stats.items() if k in active_node_ids}
    IOHandler.save_cosmograph_files(filtered_node_stats, filtered_edge_counts, SKILL_TO_GROUP)

    # 6. Summary
    print_execution_summary(len(jds), len(final_nodes_list), len(filtered_edge_counts), seniority_dist)

if __name__ == "__main__":
    process_data()