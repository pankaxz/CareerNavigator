#This utility handles the "Matching" logic. It uses Regex with word boundaries to ensure "Go" doesn't
# match "Google" and "C" doesn't match "Cloud."

import re
from typing import List, Dict, Any, Set

class TextProcessor:
    """
    @brief Utilities for processing raw text from Job Descriptions and Resumes.
    
    @details
    This class provides static methods to clean text, extract keywords, and analyze seniority levels based on heuristic scoring.
    It serves as the core linguistic engine for the DataFactory pipeline, transforming unstructured text into structured metrics.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        @brief Normalizes and sanitizes input text for processing.
        
        @details
        Performs the following operations:
        1. Converts all text to lowercase.
        2. Removes URLs to prevent false positive matches (e.g., 'go' in 'google.com').
        3. Normalizes whitespace, replacing sequences of tabs/newlines with single spaces.
        
        @param text The raw input string to clean.
        @return A normalized, lower-case string ready for regex analysis.
        """
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
        """
        @brief Analyzes a Job Description to determine the required seniority level.
        
        @details
        Uses a weighted scoring system (max score ~17.5) to classify roles into 'Junior', 'Mid', 'Senior', or 'Managerial'.
        
        <b>Scoring Categories:</b>
        - <b>Title Analysis (Max 5.0):</b> Checks for keywords like 'Senior', 'Manager', 'Head'. Managerial titles get the highest boost.
        - <b>Experience (Max 5.0):</b> Regex extraction of year requirements (e.g., "5+ years").
        - <b>Action Verbs (Max 2.0):</b> Counts strong leadership verbs (e.g., 'architect', 'orchestrate').
        - <b>Scope of Impact (Max 1.5):</b> Keywords indicating system-wide responsibility (e.g., 'distributed systems', 'scalability').
        - <b>Leadership (Max 1.5):</b> Keywords related to people management and mentorship.
        - <b>NFRs (Max 1.0):</b> Non-functional requirements like 'security', 'observability'.
        - <b>Paradigms (Max 1.0):</b> Advanced concepts like 'event-driven', 'cloud-native'.
        
        <b>Thresholds:</b>
        - **Managerial**: Explicit title match.
        - **Senior**: Score >= 9.0
        - **Mid**: Score >= 5.0
        - **Junior**: Below 5.0
        
        @param title The job title (e.g., "Senior Backend Engineer").
        @param description The full text of the job description.
        @return A dictionary containing:
            - `score` (float): The calculated seniority score.
            - `level` (str): 'Junior', 'Mid', 'Senior', or 'Managerial'.
            - `is_senior` (bool): True if level is Senior or Managerial.
        """
        score: float = 0.0
        desc_lower: str = description.lower()
        title_lower: str = title.lower()

        # 1. Base Score: Title Check (Max 5.0)
        managerial_titles: List[str] = ["manager", "director", "head", "vp", "chief", "leadership", "cto", "cio", "ciso"]
        senior_titles: List[str] = ["senior", "sr", "lead", "principal", "staff", "architect"]
        junior_titles: List[str] = ["junior", "jr", "entry", "associate", "intern", "trainee"]
        
        has_managerial_title: bool = False
        for word in managerial_titles:
            if word in title_lower:
                has_managerial_title = True
                break

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

        if has_managerial_title:
            score += 5.0 # Boost for Managerial
        elif has_senior_title:
            score += 4.0
        elif not has_junior_title:
            score += 2.5

        # 2. Base Score: Years of Experience (Max 5.0)
        senior_exp_pattern: str = r"(5\+|[5-9]|1[0-9])\s*(years|yrs|year)"
        mid_exp_pattern: str = r"(3|4)\s*(years|yrs|year)"
        
        if re.search(senior_exp_pattern, desc_lower):
            score += 5.0
        elif re.search(mid_exp_pattern, desc_lower):
            score += 2.5

        # 3. Action Verbs (Max 2.0)
        senior_verbs: List[str] = [
            "architect", "design", "lead", "mentor", "optimize", "strategize", "audit", "oversee", 
            "scale", "drive", "define", "innovate", "standardize", "champion", "modernize", 
            "orchestrate", "refactor", "pioneer", "transform", "evangelize", "govern"
        ]
        verb_count: int = 0
        for verb in senior_verbs:
            if verb in desc_lower:
                verb_count += 1
        score += min(2.0, verb_count * 0.4)

        # 4. Scope of Impact (Max 1.5)
        scope_keywords: List[str] = [
            "distributed systems", "architecture", "microservices", "scalability", "high availability", 
            "infrastructure", "security compliance", "legacy migration", "cross-functional", 
            "cloud infrastructure", "system integration", "end-to-end", "enterprise-scale"
        ]
        scope_count: int = 0
        for keyword in scope_keywords:
            if keyword in desc_lower:
                scope_count += 1
        score += min(1.5, scope_count * 0.5)

        # 5. Mentorship and Leadership (Max 1.5)
        leadership_keywords: List[str] = [
            "code review", "mentoring", "technical vision", "hiring", "onboarding", 
            "stakeholder management", "roadmap", "standardization", "team lead", 
            "technical leadership", "guiding", "facilitating"
        ]
        leadership_count: int = 0
        for keyword in leadership_keywords:
            if keyword in desc_lower:
                leadership_count += 1
        score += min(1.5, leadership_count * 0.5)

        # 6. Non-Functional Requirements (Max 1.0)
        nfr_keywords: List[str] = [
            "observability", "monitoring", "throughput", "latency", "disaster recovery", 
            "performance tuning", "cost optimization", "security audits", "reliability engineering", 
            "fault tolerance", "capacity planning"
        ]
        nfr_count: int = 0
        for keyword in nfr_keywords:
            if keyword in desc_lower:
                nfr_count += 1
        score += min(1.0, nfr_count * 0.5)

        # 7. Tooling Paradigms (Max 1.0)
        paradigm_keywords: List[str] = [
            "design patterns", "solid principles", "event-driven architecture", "serverless", 
            "cloud-native", "language agnostic", "functional programming", "object-oriented design", 
            "tdd", "ci/cd pipeline", "infrastructure as code"
        ]
        paradigm_count: int = 0
        for keyword in paradigm_keywords:
            if keyword in desc_lower:
                paradigm_count += 1
        score += min(1.0, paradigm_count * 0.5)

        # Final Classification (Scale of ~17)
        level: str = "Junior"
        if has_managerial_title:
            level = "Managerial"
        elif score >= 9.0: # Increased threshold for Senior
            level = "Senior"
        elif score >= 5.0: # Increased threshold for Mid
            level = "Mid"
        
        return {
            "score": round(score, 2),
            "level": level,
            "is_senior": score >= 9.0 or has_managerial_title
        }

    @staticmethod
    def extract_skills(text: str, skill_list: List[str]) -> List[str]:
        """
        @brief Scans text for known skills from a taxonomy list using boundary-aware regex.
        
        @details
        Iterates through the provided `skill_list` and checks for their presence in the `text`.
        Crucially uses Regex Lookarounds to support skills with special characters (like 'C++' or '.NET') which standard word boundaries (`\\b`) fail to catch.
        
        @param text The cleaned job description text.
        @param skill_list A list of skill keywords (the taxonomy universe).
        @return A unique list of skills found in the text.
        """
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

