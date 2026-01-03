from typing import List, Dict, Any

class AnalyticsEngine:
    """
    @brief Pure functional engine for calculating derived statistical metadata.
    
    @details
    Unlike `GraphBuilder`, which manages state, this class performs stateless mathematical transformations 
    on the data to produce insights (e.g., histograms, percentiles).
    """

    @staticmethod
    def calculate_seniority_distribution(seniority_scores: List[float], total_skills: int) -> Dict[str, Any]:
        """
        @brief Computes a histogram of skill seniority scores.
        
        @details
        Buckets skills into ten distinct bins ranging from 0.0 to 1.0 (e.g., "0.0-0.1", "0.9-1.0").
        This is used by the frontend to visualize the "Seniority Spread" of the entire technology universe.
        
        @param seniority_scores A list of float scores (0.0 to 1.0) derived from skill analysis.
        @param total_skills The total count of skills analyzed.
        @return A dictionary containing the histogram bucket map and total count.
        """
        distribution: Dict[str, int] = {f"{i/10:.1f}-{(i+1)/10:.1f}": 0 for i in range(10)}
        
        for score in seniority_scores:
            # Clamp score to 0.99 for bucket calculation to avoid index 10 error
            bucket_index: int = min(int(score * 10), 9)
            bucket_key: str = f"{bucket_index/10:.1f}-{(bucket_index+1)/10:.1f}"
            distribution[bucket_key] += 1

        meta: Dict[str, Any] = {
            "seniorityDistribution": distribution,
            "totalSkills": total_skills
        }
        return meta
