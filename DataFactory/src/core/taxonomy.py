import json
from typing import List, Dict
from config import cfg

class TaxonomyManager:
    """!
    @brief Manages the valid set of skills (taxonomy) taking into account Aliases and Groups.
    """
    
    # Static cache
    _TAXONOMY_CACHE = None
    _ALIAS_MAP_CACHE = None
    _GROUP_MAP_CACHE = None

    @staticmethod
    def _load_taxonomy() -> Dict:
        """Helper to load the JSON only once."""
        if TaxonomyManager._TAXONOMY_CACHE is None:
            path = cfg.get_abs_path("paths.alias_json")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    TaxonomyManager._TAXONOMY_CACHE = json.load(f)
            except FileNotFoundError:
                print(f"❌ Error: Taxonomy file not found at {path}")
                TaxonomyManager._TAXONOMY_CACHE = {}
        return TaxonomyManager._TAXONOMY_CACHE

    @staticmethod
    def get_alias_map() -> Dict[str, str]:
        """!
        @brief Builds the Master Lookup Table for Data Normalization.
        Mappings: 'term' -> 'canonical_id'.
        It flattens the taxonomy so you can look up any variant and get the ID immediately.
        """
        if TaxonomyManager._ALIAS_MAP_CACHE is not None:
            return TaxonomyManager._ALIAS_MAP_CACHE

        taxonomy = TaxonomyManager._load_taxonomy()
        alias_map = {}
        
        for group, skills in taxonomy.items():
            for canonical, aliases in skills.items():
                norm_canonical = canonical.lower()
                alias_map[norm_canonical] = norm_canonical
                
                for alias in aliases:
                    norm_alias = alias.lower()
                    alias_map[norm_alias] = norm_canonical
        
        TaxonomyManager._ALIAS_MAP_CACHE = alias_map
        return alias_map

    @staticmethod
    def get_skill_to_group_map() -> Dict[str, str]:
        """!
        @brief Maps every valid term (Canonical + Alias) to its Group. 
        It flattens the taxonomy so you can look up any variant and get the Group immediately.
        """
        if TaxonomyManager._GROUP_MAP_CACHE is not None:
            return TaxonomyManager._GROUP_MAP_CACHE

        taxonomy = TaxonomyManager._load_taxonomy()
        group_map = {}
        
        for group, skills in taxonomy.items():
            for canonical, aliases in skills.items():
                group_map[canonical.lower()] = group
                for alias in aliases:
                    group_map[alias.lower()] = group

           
        TaxonomyManager._GROUP_MAP_CACHE = group_map
        return group_map

    @staticmethod
    def get_all_skills() -> List[str]:
        """!
        @brief Returns only CANONICAL skills (for stats/reporting).
        """
        taxonomy = TaxonomyManager._load_taxonomy()
        canons = []

        for group_dict in taxonomy.values():
            canons.extend(group_dict.keys())
        
        return canons

    @staticmethod
    def get_matchable_terms() -> List[str]:
        """!
        @brief Returns ALL terms (Canonical + Aliases) sorted by Length DESC.
        """
        am = TaxonomyManager.get_alias_map()
        terms = list(am.keys())
        # Sort by length descending, then alphabetical for stability
        terms.sort(key=lambda x: (-len(x), x))
        return terms
