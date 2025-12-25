#This utility handles the "Matching" logic. It uses Regex with word boundaries to ensure "Go" doesn't
# match "Google" and "C" doesn't match "Cloud."

import re

class TextProcessor:
    @staticmethod
    def clean_text(text):
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) # Remove URLs
        text = re.sub(r'\s+', ' ', text) # Remove extra whitespace
        return text

    @staticmethod
    def detect_seniority(title, description):
        score = 0.0
        desc_lower = description.lower()
        title_lower = title.lower()

        # 1. Base Score: Title Check (Max 3.0)
        senior_titles = ["senior", "sr", "lead", "principal", "staff", "architect", "head", "manager", "vp", "director"]
        junior_titles = ["junior", "jr", "entry", "associate", "intern", "trainee"]
        
        if any(word in title_lower for word in senior_titles):
            score += 3.0
        elif not any(word in title_lower for word in junior_titles):
            score += 1.5

        # 2. Base Score: Years of Experience (Max 3.0)
        senior_exp_pattern = r"(5\+|[5-9]|1[0-9])\s*(years|yrs|year)"
        mid_exp_pattern = r"(3|4)\s*(years|yrs|year)"
        
        if re.search(senior_exp_pattern, desc_lower):
            score += 3.0
        elif re.search(mid_exp_pattern, desc_lower):
            score += 1.5

        # 3. Action Verbs (Max 1.5)
        senior_verbs = [
            "architect", "design", "lead", "mentor", "optimize", "strategize", "audit", "oversee", 
            "scale", "drive", "define", "innovate", "standardize", "champion", "modernize", 
            "orchestrate", "refactor", "pioneer", "transform", "evangelize", "govern"
        ]
        verb_count = sum(1 for verb in senior_verbs if verb in desc_lower)
        score += min(1.5, verb_count * 0.3)

        # 4. Scope of Impact (Max 1.0)
        scope_keywords = [
            "distributed systems", "architecture", "microservices", "scalability", "high availability", 
            "infrastructure", "security compliance", "legacy migration", "cross-functional", 
            "cloud infrastructure", "system integration", "end-to-end", "enterprise-scale"
        ]
        scope_count = sum(1 for keyword in scope_keywords if keyword in desc_lower)
        score += min(1.0, scope_count * 0.33)

        # 5. Mentorship and Leadership (Max 0.5)
        leadership_keywords = [
            "code review", "mentoring", "technical vision", "hiring", "onboarding", 
            "stakeholder management", "roadmap", "standardization", "team lead", 
            "technical leadership", "guiding", "facilitating"
        ]
        leadership_count = sum(1 for keyword in leadership_keywords if keyword in desc_lower)
        score += min(0.5, leadership_count * 0.25)

        # 6. Non-Functional Requirements (Max 0.5)
        nfr_keywords = [
            "observability", "monitoring", "throughput", "latency", "disaster recovery", 
            "performance tuning", "cost optimization", "security audits", "reliability engineering", 
            "fault tolerance", "capacity planning"
        ]
        nfr_count = sum(1 for keyword in nfr_keywords if keyword in desc_lower)
        score += min(0.5, nfr_count * 0.25)

        # 7. Tooling Paradigms (Max 0.5)
        paradigm_keywords = [
            "design patterns", "solid principles", "event-driven architecture", "serverless", 
            "cloud-native", "language agnostic", "functional programming", "object-oriented design", 
            "tdd", "ci/cd pipeline", "infrastructure as code"
        ]
        paradigm_count = sum(1 for keyword in paradigm_keywords if keyword in desc_lower)
        score += min(0.5, paradigm_count * 0.25)

        # Final Classification
        level = "Junior"
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
    def extract_skills(text, skill_list):
        found = set()
        clean_jd = TextProcessor.clean_text(text)
        for skill in skill_list:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, clean_jd):
                found.add(skill)
        return list(found)

