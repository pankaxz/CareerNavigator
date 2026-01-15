import re
import json
import sys
import os
from typing import List, Dict, Any, Tuple
from utils.logger import get_logger

# Try to import cfg. Dependending on run location (root vs src), path varies.
try:
    from config import cfg
except ImportError:
    # If running from root, src.config might work
    try:
        from src.config import cfg
    except ImportError:
        # Last resort: append src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), '../../src')) # Assuming src/utils/
        from config import cfg

logger = get_logger(__name__)

class SeniorityAnalyzer:
    """!
    @brief Encapsulates heuristic logic for determining job seniority.
    
    @details
    Separated from TextProcessor to maintain single responsibility principle.
    Analyzes Titles, Experience metrics, and Keyword density.
    """
    
    _SENIORITY_KEYWORDS_CACHE = None

    @staticmethod
    def _load_seniority_keywords() -> Dict[str, Any]:
        """Lazy loader for seniority keywords."""
        if SeniorityAnalyzer._SENIORITY_KEYWORDS_CACHE is not None:
            return SeniorityAnalyzer._SENIORITY_KEYWORDS_CACHE

        path = cfg.get_abs_path("paths.seniority_json") or cfg.get_abs_path("data/reference/seniority_keywords.json")
        
        if not path or not os.path.exists(path):
             logger.error(f"Seniority keywords file not found at: {path}")
             raise FileNotFoundError(f"Seniority keywords file not found at: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                SeniorityAnalyzer._SENIORITY_KEYWORDS_CACHE = json.load(f)
                logger.debug(f"Loaded seniority keywords from {path}")
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse seniority keywords from {path}: {e}")
            raise e

        return SeniorityAnalyzer._SENIORITY_KEYWORDS_CACHE

    @staticmethod
    def get_role_indicators() -> List[str]:
        """Exposes role indicators for other components (e.g. TextProcessor)."""
        keywords = SeniorityAnalyzer._load_seniority_keywords()
        return keywords.get("role_indicators", [])

    @staticmethod
    def get_title_keywords() -> List[str]:
        """Exposes flattened list of all seniority keywords (senior, managerial, junior)."""
        keywords = SeniorityAnalyzer._load_seniority_keywords()
        titles = keywords.get("titles", {})
        
        all_keywords = []
        all_keywords.extend(titles.get("senior", []))
        all_keywords.extend(titles.get("managerial", []))
        all_keywords.extend(titles.get("junior", []))
        
        return all_keywords

    @staticmethod
    def get_stopwords() -> List[str]:
        """Exposes stopwords for other components (e.g. "role", "job", "title", "position", "senior")."""
        # Base stopwords
        stopwords = {
            "role", "job", "title", "position", "senior", "staff", "engineer", "lead", "manager", 
            "sr", "jr", "team", "meet", "description"
        }
        # Note: Removed "ii", "iii" to allow numeric suffixes to count
        return list(stopwords)

    @staticmethod
    def _analyze_title(title_lower: str, keywords: Dict[str, Any]) -> Tuple[float, bool]:
        """Calculates score based on job title."""
        managerial_titles = keywords["titles"]["managerial"]
        senior_titles = keywords["titles"]["senior"]
        junior_titles = keywords["titles"]["junior"]
        
        has_managerial = any(word in title_lower for word in managerial_titles)
        has_senior = any(word in title_lower for word in senior_titles)
        has_junior = any(word in title_lower for word in junior_titles)

        score = 0.0
        if has_managerial:
            score = 5.0
        elif has_senior:
            score = 4.0
        elif not has_junior:
            score = 2.5
            
        return score, has_managerial

    @staticmethod
    def _analyze_experience(desc_lower: str) -> float:
        """Calculates score based on years of experience regex."""
        senior_exp_pattern = r"(5\+|[5-9]|1[0-9])\s*(years|yrs|year)"
        mid_exp_pattern = r"(3|4)\s*(years|yrs|year)"
        
        if re.search(senior_exp_pattern, desc_lower):
            return 5.0
        elif re.search(mid_exp_pattern, desc_lower):
            return 2.5
        return 0.0

    @staticmethod
    def _calculate_keyword_score(text_lower: str, keywords_list: List[str], multiplier: float, max_cap: float) -> float:
        """Generic scoring for keyword categories."""
        count = sum(1 for word in keywords_list if word in text_lower)
        return min(max_cap, count * multiplier)

    @staticmethod
    def detect_seniority(title: str, description: str) -> Dict[str, Any]:
        """!
        @brief Analyzes a Job Description to determine the required seniority level.
        @details Uses weighted scoring system from loaded keywords.
        """
        desc_lower = description.lower()
        title_lower = title.lower()
        
        keywords = SeniorityAnalyzer._load_seniority_keywords()

        # 1. Base Score: Title Check (Max 5.0)
        title_score, has_managerial_title = SeniorityAnalyzer._analyze_title(title_lower, keywords)
        
        # 2. Base Score: Years of Experience (Max 5.0)
        experience_score = SeniorityAnalyzer._analyze_experience(desc_lower)
        
        # 3. Action Verbs (Max 2.0)
        verb_score = SeniorityAnalyzer._calculate_keyword_score(
            desc_lower, keywords["action_verbs"], multiplier=0.4, max_cap=2.0
        )

        # 4. Scope of Impact (Max 1.5)
        scope_score = SeniorityAnalyzer._calculate_keyword_score(
            desc_lower, keywords["scope_keywords"], multiplier=0.5, max_cap=1.5
        )

        # 5. Mentorship and Leadership (Max 1.5)
        leadership_score = SeniorityAnalyzer._calculate_keyword_score(
            desc_lower, keywords["leadership_keywords"], multiplier=0.5, max_cap=1.5
        )

        # 6. Non-Functional Requirements (Max 1.0)
        nfr_score = SeniorityAnalyzer._calculate_keyword_score(
            desc_lower, keywords["nfr_keywords"], multiplier=0.5, max_cap=1.0
        )

        # 7. Tooling Paradigms (Max 1.0)
        paradigm_score = SeniorityAnalyzer._calculate_keyword_score(
            desc_lower, keywords["paradigm_keywords"], multiplier=0.5, max_cap=1.0
        )

        total_score = (
            title_score + experience_score + verb_score + 
            scope_score + leadership_score + nfr_score + paradigm_score
        )

        # Final Classification
        level = "Junior"
        if has_managerial_title:
            level = "Managerial"
        elif total_score >= 9.0:
            level = "Senior"
        elif total_score >= 5.0:
            level = "Mid"
        
        return {
            "score": round(total_score, 2),
            "level": level,
            "is_senior": total_score >= 9.0 or has_managerial_title
        }
