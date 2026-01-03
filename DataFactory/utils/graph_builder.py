from typing import List, Dict, Tuple, Any
from collections import Counter
import itertools

class GraphBuilder:
    """
    @brief Aggregates raw skill occurrences into a statistical graph structure.
    
    @details
    Responsible for maintaining the in-memory state of the graph during processing.
    It tracks:
    -   **Nodes**: Counts of individual skills, separated by seniority contexts (Senior, Managerial).
    -   **Edges**: Co-occurrence counts between pairs of skills found in the same JD.
    """

    @staticmethod
    def initialize_stats(all_skills: List[str]) -> Tuple[Dict[str, Dict[str, int]], Dict[Tuple[str, str], Dict[str, int]], Counter]:
        """
        @brief Initializes the data structures required for graph construction.
        
        @details
        Pre-populates the `node_stats` dictionary for every skill in the taxonomy to ensure O(1) lookups.
        
        @param all_skills List of all valid skill identifiers.
        @return A tuple containing:
            - `node_stats` (Dict): Storage for node metrics. Structure: `{ "skill": { "total": 0, "senior_count": 0, "managerial_count": 0 } }`
            - `edge_counts` (Dict): Storage for edge metrics. Structure: `{ ("skill_a", "skill_b"): { ... } }`
            - `seniority_dist` (Counter): A counter for tracking job distribution by level.
        """
        # Node Stats: { "skill_name": { "total": 0, "senior_count": 0, "managerial_count": 0 } }
        node_stats: Dict[str, Dict[str, int]] = {}
        for skill in all_skills:
            node_stats[skill] = {"total": 0, "senior_count": 0, "managerial_count": 0}
        
        # Edge Counts: { ("skill_a", "skill_b"): { "total": 0, "senior_count": 0, "managerial_count": 0 } }
        edge_counts: Dict[Tuple[str, str], Dict[str, int]] = {}
        
        seniority_dist: Counter = Counter()
        
        return node_stats, edge_counts, seniority_dist

    @staticmethod
    def update_metrics(
        node_stats: Dict[str, Dict[str, int]], 
        edge_counts: Dict[Tuple[str, str], Dict[str, int]], 
        found_skills: List[str], 
        level: str
    ) -> None:
        """
        @brief Updates the graph statistics with data from a single Job Description.
        
        @details
        This is the core aggregation logic. It performs two main tasks:
        1.  **Node Updates**: Increments the total count for each found skill. If the JD is Senior/Managerial, increments those specific counters too.
        2.  **Edge Updates**: Generating a complete subgraph (clique) for the found skills. Every unique pair of skills increments an edge weight.
        
        @param node_stats Mutable dictionary of node statistics.
        @param edge_counts Mutable dictionary of edge statistics.
        @param found_skills List of skills found in the current JD.
        @param level The seniority level of the current JD (e.g., 'Senior', 'Managerial', 'Junior').
        """
        
        is_senior = level == "Senior" or level == "Managerial"
        is_managerial = level == "Managerial"

        # Update Node Stats
        for skill in found_skills:
            node_stats[skill]["total"] += 1
            if is_senior:
                node_stats[skill]["senior_count"] += 1
            if is_managerial:
                node_stats[skill]["managerial_count"] += 1
                
        # Update Edge Stats (Co-occurrences)
        if len(found_skills) > 1:
            # Sort to ensure (A, B) is same as (B, A)
            sorted_skills: List[str] = sorted(found_skills)
            for pair in itertools.combinations(sorted_skills, 2):
                if pair not in edge_counts:
                    edge_counts[pair] = {"total": 0, "senior_count": 0, "managerial_count": 0}
                
                edge_counts[pair]["total"] += 1
                if is_senior:
                    edge_counts[pair]["senior_count"] += 1
                if is_managerial:
                    edge_counts[pair]["managerial_count"] += 1

    @staticmethod
    def prepare_nodes_list(
        node_stats: Dict[str, Dict[str, int]], 
        skill_to_group: Dict[str, str], 
        threshold: int
    ) -> Tuple[List[Dict[str, Any]], List[str], List[float]]:
        """
        @brief Transforms raw node statistics into the final list of node objects.
        
        @details
        Filters out skills that appeared fewer times than the threshold.
        Calculates derived metrics like `seniorityScore` (senior_count / total) and `managerialScore`.
        
        @param node_stats The raw statistical data.
        @param skill_to_group Mapping for assigning group categories to nodes.
        @param threshold Minimum number of appearances to survive filtration.
        @return A tuple of:
            - `nodes_list`: List of final node dictionaries ready for JSON serialization.
            - `active_node_ids`: List of IDs of nodes that survived filtering.
            - `seniority_scores`: List of all seniority scores (used for global distribution calculation).
        """
        
        nodes_list: List[Dict[str, Any]] = []
        active_node_ids: List[str] = []
        seniority_scores: List[float] = []
        
        for skill, stats in node_stats.items():
            if stats["total"] >= threshold:
                active_node_ids.append(skill)
                seniority_score: float = round(stats["senior_count"] / stats["total"], 2)
                managerial_score: float = round(stats["managerial_count"] / stats["total"], 2)
                
                seniority_scores.append(seniority_score)
                nodes_list.append({
                    "id": skill,
                    "group": skill_to_group.get(skill, "Unknown"),
                    "val": stats["total"],
                    "seniorityScore": seniority_score,
                    "managerialScore": managerial_score,
                    "isSenior": seniority_score > 0.6,
                    "isManagerial": managerial_score > 0.4 # Threshold for "Managerial" designation
                })
                
        return nodes_list, active_node_ids, seniority_scores

    @staticmethod
    def filter_edges(
        edge_counts: Dict[Tuple[str, str], Dict[str, int]], 
        active_node_ids: List[str],
        threshold: int
    ) -> Dict[Tuple[str, str], Dict[str, int]]:
        """
        @brief Prunes edges that connect to culled nodes or do not meet the weight threshold.
        
        @details
        Ensures strict referential integrity; an edge cannot exist if one of its nodes has been filtered out.
        
        @param edge_counts The raw edge statistics.
        @param active_node_ids List of valid node IDs that survived filtering.
        @param threshold Minimum edge weight to survive filtering.
        @return A filtered dictionary of edges.
        """
        
        filtered_edge_counts: Dict[Tuple[str, str], Dict[str, int]] = {}
        active_node_set = set(active_node_ids) # For faster lookups
        
        for (src, tgt), stats in edge_counts.items():
            if src in active_node_set and tgt in active_node_set:
                if stats["total"] >= threshold:
                    filtered_edge_counts[(src, tgt)] = stats
        return filtered_edge_counts
