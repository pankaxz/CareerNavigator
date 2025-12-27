from pdb import line_prefix
import json
import csv
import os
from typing import List, Dict, Any, Tuple

class IOHandler:
    @staticmethod
    def load_raw_jds(file_path: str = "raw_jds.txt", delimiter: str = "###END###") -> List[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content: str = f.read()
                # Split and clean
                # Original: jds = [jd.strip() for jd in content.split(delimiter) if jd.strip()]
                raw_segments: List[str] = content.split(delimiter)
                jds: List[str] = []
                for segment in raw_segments:
                    cleaned_segment: str = segment.strip()
                    if cleaned_segment:
                        jds.append(cleaned_segment)
                return jds
                
        except FileNotFoundError:
            print(f"❌ Error: {file_path} not found!")
            return []

    @staticmethod
    def ensure_output_dir(output_dir: str) -> None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def save_universe(nodes_list: List[Dict[str, Any]], edge_counts: Dict[Tuple[str, str], Dict[str, int]], meta: Dict[str, Any] = None, output_dir: str = "output") -> None:
        IOHandler.ensure_output_dir(output_dir)
        
        links_list: List[Dict[str, Any]] = []
        for (src, tgt), stats in edge_counts.items():
            if stats["total"] > 0:
                seniority_score: float = round(stats["senior_count"] / stats["total"], 2)
                links_list.append({
                    "source": src,
                    "target": tgt,
                    "value": stats["total"],
                    "seniorityScore": seniority_score,
                    "isSenior": seniority_score > 0.6
                })

        # Structure matches the C# Model expectations
        universe_json: Dict[str, Any] = {
            "meta": meta if meta else {},
            "nodes": nodes_list,
            "links": links_list
        }

        output_path: str = os.path.join(output_dir, "universe.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(universe_json, f, indent=4)
        print(f"✅ Created {output_path}")


    @staticmethod
    def save_cosmograph_files(node_stats: Dict[str, Dict[str, int]], edge_counts: Dict[Tuple[str, str], Dict[str, int]], skill_to_group: Dict[str, str], output_dir: str = "output") -> None:
        IOHandler.ensure_output_dir(output_dir)

        # Nodes CSV
        nodes_path: str = os.path.join(output_dir, "nodes.csv")
        with open(nodes_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "group", "val"]) # Header
            for skill, stats in node_stats.items():
                if stats["total"] > 0:
                    writer.writerow([skill, skill_to_group[skill], stats["total"]])
        print(f"✅ Created {nodes_path}")

        # Edges CSV
        edges_path: str = os.path.join(output_dir, "edges.csv")
        with open(edges_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target", "value"]) # Header
            # edge_counts is now a dict of dicts: { (src, tgt): {total, senior_count} }
            for (src, tgt), stats in edge_counts.items():
                writer.writerow([src, tgt, stats["total"]])
        print(f"✅ Created {edges_path}")