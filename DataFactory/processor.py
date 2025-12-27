from typing import List, Dict, Tuple, Any
from collections import Counter
from utils.text_processor import TextProcessor
from utils.io_handler import IOHandler
from utils.taxonomy_manager import TaxonomyManager
from utils.graph_builder import GraphBuilder
from utils.analytics_engine import AnalyticsEngine

# --- Global Constants (Configuration) ---
ALL_SKILLS: List[str] = TaxonomyManager.get_all_skills()
SKILL_TO_GROUP: Dict[str, str] = TaxonomyManager.get_skill_to_group_map()
THRESHOLD: int = 1

# --- Core Logic Step 1: Analyze Single JD ---
def analyze_jd_content(jd_text: str) -> Tuple[List[str], bool, str]:
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
    print(f"\n✨ Done! Processed {jds_count} JDs.")
    print(f"Found {nodes_count} filtered skills (Threshold: {THRESHOLD}) and {edges_count} filtered edges")
    print("📊 Seniority Distribution:")
    for level, count in seniority_dist.items():
        print(f"  - {level}: {count}")

# --- Orchestrator ---
def process_data() -> None:
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
        GraphBuilder.update_metrics(node_stats, edge_counts, found_skills, is_senior)

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