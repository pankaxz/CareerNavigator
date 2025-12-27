from typing import List, Dict, Any

class AnalyticsEngine:
    @staticmethod
    def calculate_seniority_distribution(seniority_scores: List[float], total_skills: int) -> Dict[str, Any]:
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
