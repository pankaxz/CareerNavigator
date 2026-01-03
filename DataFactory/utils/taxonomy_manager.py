from typing import List, Dict
from output.taxonomy import TAXONOMY

class TaxonomyManager:
    """
    @brief Manages the valid set of skills (taxonomy) that the system recognizes.
    
    @details
    Serves as the Single Source of Truth for:
    1.  <b>Skill Dictionary</b>: What keywords constitute a "skill" (e.g., "Python", "Kubernetes").
    2.  <b>Grouping</b>: Which category a skill belongs to (e.g., "Languages", "Cloud_Platforms").
    
    This abstractions allows the underlying JSON/Python taxonomy file to change structure without breaking the rest of the pipeline.
    """

    @staticmethod
    def get_all_skills() -> List[str]:
        """
        @brief Retrieves a flat list of all skill keywords.
        
        @return A list of strings representing every skill in the known universe.
        """
        skills: List[str] = []
        for sublist in TAXONOMY.values():
            for skill in sublist:
                skills.append(skill)
                # Removed print statement to reduce console noise during production runs
        return skills


    @staticmethod
    def get_skill_to_group_map() -> Dict[str, str]:
        """
        @brief Creates a reverse-lookup map to find the category of a given skill.
        
        @details
        Iterates through the hierarchical `TAXONOMY` to build a flat dictionary:
        `{ "python": "Languages", "aws": "Cloud_Platforms", ... }`
        This is essential for the `GraphBuilder` to assign group attributes to nodes.
        
        @return A dictionary mapping 'skill_name' -> 'group_name'.
        """
        mapping: Dict[str, str] = {}
        for group, skills in TAXONOMY.items():
            for skill in skills:
                mapping[skill] = group
                # Removed print statement to reduce console noise
        return mapping
