#This utility handles the "Matching" logic. It uses Regex with word boundaries to ensure "Go" doesn't
# match "Google" and "C" doesn't match "Cloud."

import re
from typing import List, Dict, Any, Set

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = text.lower()
        
        # --- Regex: URL Removal ---
        # Pattern: http\S+ | www\S+ | https\S+
        # - \S+ matches any non-whitespace character until a space is found.
        # - This effectively strips out links so they don't interfere with skill detection.
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) 

        # --- Regex: Whitespace Normalization ---
        # Pattern: \s+
        # - \s+ matches one or more whitespace characters (spaces, tabs, newlines).
        # - Replacing them with a single space ensures consistent word-boundary matching.
        text = re.sub(r'\s+', ' ', text) 
        
        return text

    @staticmethod
    def detect_seniority(title: str, description: str) -> Dict[str, Any]:
        score: float = 0.0
        desc_lower: str = description.lower()
        title_lower: str = title.lower()

        # 1. Base Score: Title Check (Max 3.0)
        senior_titles: List[str] = ["senior", "sr", "lead", "principal", "staff", "architect", "head", "manager", "vp", "director"]
        junior_titles: List[str] = ["junior", "jr", "entry", "associate", "intern", "trainee"]
        
        # Explicit loop for senior title check
        has_senior_title: bool = False
        for word in senior_titles:
            if word in title_lower:
                has_senior_title = True
                break
        
        has_junior_title: bool = False
        for word in junior_titles:
            if word in title_lower:
                has_junior_title = True
                break

        if has_senior_title:
            score += 3.0
        elif not has_junior_title:
            score += 1.5

        # 2. Base Score: Years of Experience (Max 3.0)
        
        # --- Regex: Senior Experience Detection ---
        # Pattern: (5\+|[5-9]|1[0-9])\s*(years|yrs|year)
        # - (5\+|[5-9]|1[0-9]): Matches '5+', individual digits 5-9, or teen numbers 10-19.
        # - \s*: Matches zero or more whitespace characters.
        # - (years|yrs|year): Matches any of the common experience suffixes.
        senior_exp_pattern: str = r"(5\+|[5-9]|1[0-9])\s*(years|yrs|year)"

        # --- Regex: Mid-Level Experience Detection ---
        # Pattern: (3|4)\s*(years|yrs|year)
        # - (3|4): Matches the digit 3 or 4.
        mid_exp_pattern: str = r"(3|4)\s*(years|yrs|year)"
        
        if re.search(senior_exp_pattern, desc_lower):
            score += 3.0
        elif re.search(mid_exp_pattern, desc_lower):
            score += 1.5

        # 3. Action Verbs (Max 1.5)
        senior_verbs: List[str] = [
            "architect", "design", "lead", "mentor", "optimize", "strategize", "audit", "oversee", 
            "scale", "drive", "define", "innovate", "standardize", "champion", "modernize", 
            "orchestrate", "refactor", "pioneer", "transform", "evangelize", "govern"
        ]
        verb_count: int = 0
        for verb in senior_verbs:
            if verb in desc_lower:
                verb_count += 1
        score += min(1.5, verb_count * 0.3)

        # 4. Scope of Impact (Max 1.0)
        scope_keywords: List[str] = [
            "distributed systems", "architecture", "microservices", "scalability", "high availability", 
            "infrastructure", "security compliance", "legacy migration", "cross-functional", 
            "cloud infrastructure", "system integration", "end-to-end", "enterprise-scale"
        ]
        scope_count: int = 0
        for keyword in scope_keywords:
            if keyword in desc_lower:
                scope_count += 1
        score += min(1.0, scope_count * 0.33)

        # 5. Mentorship and Leadership (Max 0.5)
        leadership_keywords: List[str] = [
            "code review", "mentoring", "technical vision", "hiring", "onboarding", 
            "stakeholder management", "roadmap", "standardization", "team lead", 
            "technical leadership", "guiding", "facilitating"
        ]
        leadership_count: int = 0
        for keyword in leadership_keywords:
            if keyword in desc_lower:
                leadership_count += 1
        score += min(0.5, leadership_count * 0.25)

        # 6. Non-Functional Requirements (Max 0.5)
        nfr_keywords: List[str] = [
            "observability", "monitoring", "throughput", "latency", "disaster recovery", 
            "performance tuning", "cost optimization", "security audits", "reliability engineering", 
            "fault tolerance", "capacity planning"
        ]
        nfr_count: int = 0
        for keyword in nfr_keywords:
            if keyword in desc_lower:
                nfr_count += 1
        score += min(0.5, nfr_count * 0.25)

        # 7. Tooling Paradigms (Max 0.5)
        paradigm_keywords: List[str] = [
            "design patterns", "solid principles", "event-driven architecture", "serverless", 
            "cloud-native", "language agnostic", "functional programming", "object-oriented design", 
            "tdd", "ci/cd pipeline", "infrastructure as code"
        ]
        paradigm_count: int = 0
        for keyword in paradigm_keywords:
            if keyword in desc_lower:
                paradigm_count += 1
        score += min(0.5, paradigm_count * 0.25)

        # Final Classification
        level: str = "Junior"
        if score >= 6.0:
            level = "Senior"
        elif score >= 3.0:
            level = "Mid"
        
        return {
            "score": round(score, 2),
            "level": level,
            "is_senior": score >= 6.0
        }

    @staticmethod
    def extract_skills(text: str, skill_list: List[str]) -> List[str]:
        found: Set[str] = set()
        clean_jd: str = TextProcessor.clean_text(text)
        for skill in skill_list:
            # --- Regex: Improved Skill Matching ---
            # Replaced \b with lookarounds (?<!\w) and (?!\w) to handle skills with symbols (e.g., C++, .NET, C#)
            # - (?<!\w): Negative lookbehind. Ensures the character BEFORE the skill is NOT a word char.
            # - re.escape(skill): Safely handles skills with special regex characters.
            # - (?!\w): Negative lookahead. Ensures the character AFTER the skill is NOT a word char.
            # This works for "C++" (next char is space/punctuation, not a word char) whereas \b failed because '+' is a non-word char.
            pattern: str = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
            
            if re.search(pattern, clean_jd):
                found.add(skill)
        return list(found)

