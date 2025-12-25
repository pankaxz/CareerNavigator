import json
import itertools
import csv
from collections import Counter
import re
from output.taxonomy import TAXONOMY
from utils.text_processor import TextProcessor
from utils.io_handler import IOHandler

# Flatten for fast searching
ALL_SKILLS = [skill for sublist in TAXONOMY.values() for skill in sublist]
SKILL_TO_GROUP = {skill: group for group, skills in TAXONOMY.items() for skill in skills}

def process_data():
    # Use a dictionary to track stats per skill
    # Structure: { "skill_name": { "total": 0, "senior_count": 0 } }
    node_stats = {skill: {"total": 0, "senior_count": 0} for skill in ALL_SKILLS}
    # Structure: { ("skill_a", "skill_b"): { "total": 0, "senior_count": 0 } }
    edge_counts = {}
    seniority_dist = Counter()

    print("🚀 Starting Data Factory...")
    
    # 1. Load Raw JDs
    jds = IOHandler.load_raw_jds()
    if not jds:
        return

    print(f"📖 Found {len(jds)} Job Descriptions. Analyzing...")

    # 2. Extract Skills and Co-occurrences
    for jd in jds:
        # Detect Seniority
        lines = jd.split('\n')
        title = lines[0] if lines else ""
        seniority_info = TextProcessor.detect_seniority(title, jd)
        is_senior_jd = seniority_info['is_senior']
        seniority_dist[seniority_info['level']] += 1

        # Extract Skills using TextProcessor    
        found_in_jd = TextProcessor.extract_skills(jd, ALL_SKILLS)
        
        # Update node stats
        for skill in found_in_jd:
            node_stats[skill]["total"] += 1
            if is_senior_jd:
                node_stats[skill]["senior_count"] += 1
        
        # Unique skills only per JD to avoid double-counting links
        if len(found_in_jd) > 1:
            for pair in itertools.combinations(sorted(found_in_jd), 2):
                if pair not in edge_counts:
                    edge_counts[pair] = {"total": 0, "senior_count": 0}
                
                edge_counts[pair]["total"] += 1
                if is_senior_jd:
                    edge_counts[pair]["senior_count"] += 1

    # 3. Create the JSON Object (For React/C#)
    nodes_list = []
    for skill, stats in node_stats.items():
        if stats["total"] > 0:
            seniority_score = round(stats["senior_count"] / stats["total"], 2)
            nodes_list.append({
                "id": skill,
                "group": SKILL_TO_GROUP[skill],
                "val": stats["total"],
                "seniorityScore": seniority_score,
                "isSenior": seniority_score > 0.6
            })

    # 4. Use IOHandler for Exports
    IOHandler.save_universe(nodes_list, edge_counts)
    IOHandler.save_cosmograph_files(node_stats, edge_counts, SKILL_TO_GROUP)

    print(f"\n✨ Done! Processed {len(jds)} JDs.")
    print(f"Found {len(nodes_list)} skills and {len(edge_counts)}")
    print("� Starting Data Factory...")
    for level, count in seniority_dist.items():
        print(f"  - {level}: {count}")

if __name__ == "__main__":
    process_data()