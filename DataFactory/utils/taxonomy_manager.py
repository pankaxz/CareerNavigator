from typing import List, Dict
from output.taxonomy import TAXONOMY

class TaxonomyManager:
    @staticmethod
    def get_all_skills() -> List[str]:
        skills: List[str] = []
        for sublist in TAXONOMY.values():
            for skill in sublist:
                skills.append(skill)
                print(skill)
        return skills


    @staticmethod
    def get_skill_to_group_map() -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for group, skills in TAXONOMY.items():
            for skill in skills:
                mapping[skill] = group
                print(group, skill)
        return mapping
