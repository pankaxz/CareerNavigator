from typing import List, Dict, Tuple, Any
from collections import Counter
import itertools

class GraphBuilder:
    @staticmethod
    def initialize_stats(all_skills: List[str]) -> Tuple[Dict[str, Dict[str, int]], Dict[Tuple[str, str], Dict[str, int]], Counter]:
        # Node Stats: { "skill_name": { "total": 0, "senior_count": 0 } }
        node_stats: Dict[str, Dict[str, int]] = {}
        for skill in all_skills:
            node_stats[skill] = {"total": 0, "senior_count": 0}
        
        # Edge Counts: { ("skill_a", "skill_b"): { "total": 0, "senior_count": 0 } }
        edge_counts: Dict[Tuple[str, str], Dict[str, int]] = {}
        
        seniority_dist: Counter = Counter()
        
        return node_stats, edge_counts, seniority_dist

    @staticmethod
    def update_metrics(
        node_stats: Dict[str, Dict[str, int]], 
        edge_counts: Dict[Tuple[str, str], Dict[str, int]], 
        found_skills: List[str], 
        is_senior: bool
    ) -> None:
        
        # Update Node Stats
        for skill in found_skills:
            node_stats[skill]["total"] += 1
            if is_senior:
                node_stats[skill]["senior_count"] += 1
                
        # Update Edge Stats (Co-occurrences)
        if len(found_skills) > 1:
            # Sort to ensure (A, B) is same as (B, A)
            sorted_skills: List[str] = sorted(found_skills)
            for pair in itertools.combinations(sorted_skills, 2):
                if pair not in edge_counts:
                    edge_counts[pair] = {"total": 0, "senior_count": 0}
                
                edge_counts[pair]["total"] += 1
                if is_senior:
                    edge_counts[pair]["senior_count"] += 1

    @staticmethod
    def prepare_nodes_list(
        node_stats: Dict[str, Dict[str, int]], 
        skill_to_group: Dict[str, str], 
        threshold: int
    ) -> Tuple[List[Dict[str, Any]], List[str], List[float]]:
        
        nodes_list: List[Dict[str, Any]] = []
        active_node_ids: List[str] = []
        seniority_scores: List[float] = []
        
        for skill, stats in node_stats.items():
            if stats["total"] >= threshold:
                active_node_ids.append(skill)
                seniority_score: float = round(stats["senior_count"] / stats["total"], 2)
                seniority_scores.append(seniority_score)
                nodes_list.append({
                    "id": skill,
                    "group": skill_to_group.get(skill, "Unknown"),
                    "val": stats["total"],
                    "seniorityScore": seniority_score,
                    "isSenior": seniority_score > 0.6
                })
                
        return nodes_list, active_node_ids, seniority_scores

    @staticmethod
    def filter_edges(
        edge_counts: Dict[Tuple[str, str], Dict[str, int]], 
        active_node_ids: List[str],
        threshold: int
    ) -> Dict[Tuple[str, str], Dict[str, int]]:
        
        filtered_edge_counts: Dict[Tuple[str, str], Dict[str, int]] = {}
        active_node_set = set(active_node_ids) # For faster lookups
        
        for (src, tgt), stats in edge_counts.items():
            if src in active_node_set and tgt in active_node_set:
                if stats["total"] >= threshold:
                    filtered_edge_counts[(src, tgt)] = stats
        return filtered_edge_counts
