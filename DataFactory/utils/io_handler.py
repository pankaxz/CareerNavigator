import json
import csv
import os

class IOHandler:
    @staticmethod
    def load_raw_jds(file_path="raw_jds.txt", delimiter="###END###"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Split and clean
                jds = [jd.strip() for jd in content.split(delimiter) if jd.strip()]
                return jds
        except FileNotFoundError:
            print(f"❌ Error: {file_path} not found!")
            return []

    @staticmethod
    def ensure_output_dir(output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def save_universe(nodes_list, edge_counts, output_dir="output"):
        IOHandler.ensure_output_dir(output_dir)
        
        links_list = []
        for (src, tgt), stats in edge_counts.items():
            if stats["total"] > 0:
                seniority_score = round(stats["senior_count"] / stats["total"], 2)
                links_list.append({
                    "source": src,
                    "target": tgt,
                    "value": stats["total"],
                    "seniorityScore": seniority_score,
                    "isSenior": seniority_score > 0.6
                })

        # Structure matches the C# Model expectations
        universe_json = {
            "nodes": nodes_list,
            "links": links_list
        }

        output_path = os.path.join(output_dir, "universe.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(universe_json, f, indent=4)
        print(f"✅ Created {output_path}")

    @staticmethod
    def save_cosmograph_files(node_stats, edge_counts, skill_to_group, output_dir="output"):
        IOHandler.ensure_output_dir(output_dir)

        # Nodes CSV
        nodes_path = os.path.join(output_dir, "nodes.csv")
        with open(nodes_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "group", "val"]) # Header
            for skill, stats in node_stats.items():
                if stats["total"] > 0:
                    writer.writerow([skill, skill_to_group[skill], stats["total"]])
        print(f"✅ Created {nodes_path}")

        # Edges CSV
        edges_path = os.path.join(output_dir, "edges.csv")
        with open(edges_path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["source", "target", "value"]) # Header
            # edge_counts is now a dict of dicts: { (src, tgt): {total, senior_count} }
            for (src, tgt), stats in edge_counts.items():
                writer.writerow([src, tgt, stats["total"]])
        print(f"✅ Created {edges_path}")