from pdb import line_prefix
import json
import csv
import os
from typing import List, Dict, Any, Tuple

class IOHandler:
    """!
    @brief Abstraction layer for File Input/Output operations.
    
    @details
    Centralizes all disk operations including:
    - Reading raw job descriptions from text files.
    - Saving the structural graph data to JSON (for the application).
    - Saving CSV exports (for visualization tools like Cosmograph).
    - Managing directory creation.
    """

    @staticmethod
    def load_raw_jds(file_path: str = "raw_jds.txt", delimiter: str = "###END###") -> List[str]:
        """!
        @brief Loads and segments raw job description data.
        
        @details
        Reads a single large text file containing multiple JDs separated by a custom delimiter.
        Robustly handles empty segments and whitespace.
        
        @param file_path Path to the raw text file (default: "raw_jds.txt").
        @param delimiter The string marker used to separate distinct JDs (default: "###END###").
        @return A list of strings, where each string is one full job description. Returns empty list on error.
        """
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
        """!
        @brief Ensures the target output directory exists.
        
        @details
        Idempotent operation: creates the directory if missing, does nothing if it exists.
        
        @param output_dir Path to the directory.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def save_universe(nodes_list: List[Dict[str, Any]], edge_counts: Dict[Tuple[str, str], Dict[str, int]], meta: Dict[str, Any] = None, output_dir: str = "output") -> None:
        """!
        @brief Serializes the graph data into the canonical `universe.json` format.
        
        @details
        This is the primary output of the DataFactory. The JSON structure is designed to be directly consumable by the C# `UniverseProvider`.
        It transforms the internal edge dictionary map into a list of link objects containing calculated metadata (seniority score, managerial score).
        
        @param nodes_list List of node objects.
        @param edge_counts Dictionary of edge statistics.
        @param meta Optional dictionary of global metadata (e.g., seniority distribution histograms).
        @param output_dir Target directory for saving the file.
        """
        IOHandler.ensure_output_dir(output_dir)
        
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
        """!
        @brief Exports graph data to CSV format optimized for Cosmograph.app.
        
        @details
        Generates two files:
        1.  `nodes.csv`: Columns `id`, `group`, `val` (weight).
        2.  `edges.csv`: Columns `source`, `target`, `value` (weight).
        
        @param node_stats Dictionary of raw node stats.
        @param edge_counts Dictionary of raw edge stats.
        @param skill_to_group Taxonomy mapping for group column.
        @param output_dir Target directory.
        """
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