import json
import csv
import os
from typing import List, Dict, Any, Tuple

class Writer:
    """!
    @brief Operations for writing data.
    """

    @staticmethod
    def ensure_output_dir(output_dir: str) -> None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def save_universe(nodes_list: List[Dict[str, Any]], edge_counts: Dict[Tuple[str, str], Dict[str, int]], meta: Dict[str, Any] = None, output_dir: str = "data/output") -> None:
        """!
        @brief Serializes the graph data into the canonical `universe.json` format.
        """
        Writer.ensure_output_dir(output_dir)
        
        links_list: List[Dict[str, Any]] = []
        for (src, tgt), stats in edge_counts.items():
            if stats["total"] > 0:
                seniority_score: float = round(stats["senior_count"] / stats["total"], 2)
                managerial_score: float = round(stats["managerial_count"] / stats["total"], 2)

                links_list.append({
                    "source": src,
                    "target": tgt,
                    "value": stats["total"],
                    "seniorityScore": seniority_score,
                    "managerialScore": managerial_score,
                    "isSenior": seniority_score > 0.6,
                    "isManagerial": managerial_score > 0.4
                })

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
    def save_cosmograph_files(node_stats: Dict[str, Dict[str, int]], edge_counts: Dict[Tuple[str, str], Dict[str, int]], skill_to_group: Dict[str, str], output_dir: str = "data/output") -> None:
        """!
        @brief Exports graph data to CSV format optimized for Cosmograph.app.
        """
        Writer.ensure_output_dir(output_dir)

        # Nodes CSV
        nodes_path: str = os.path.join(output_dir, "nodes.csv")
        with open(nodes_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "group", "val"]) # Header
            for skill, stats in node_stats.items():
                if stats["total"] > 0:
                    writer.writerow([skill, skill_to_group.get(skill, "Unknown"), stats["total"]])
        print(f"✅ Created {nodes_path}")

        # Edges CSV
        edges_path: str = os.path.join(output_dir, "edges.csv")
        with open(edges_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target", "value"]) # Header
            for (src, tgt), stats in edge_counts.items():
                writer.writerow([src, tgt, stats["total"]])
        print(f"✅ Created {edges_path}")
