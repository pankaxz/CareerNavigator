import logging
import re
from typing import List, Dict, Set
from utils.seniority_analyzer import SeniorityAnalyzer
from utils.logger import get_logger

logger = get_logger(__name__)

class TextProcessor:
    """!
    @brief Utilities for processing raw text from Job Descriptions and Resumes.
    
    @details
    This class provides static methods to clean text and extract keywords.
    Seniority analysis logic has been moved to SeniorityAnalyzer.
    """

    @staticmethod
    def _calculate_title_density(title: str, text: str) -> float:
        """Calculates how strongly a title is supported by the body text."""
        # Normalize and tokenize
        stopwords = SeniorityAnalyzer.get_stopwords()
        words = [w.lower() for w in title.split() if w.lower() not in stopwords and len(w) > 2]
        
        if not words:
            logger.debug(f"Density calc: No significant words found in title '{title}' (after stopword removal). Returning 0.0")
            return 0.0
            
        text_lower = text.lower()
        score = 0.0
        for word in words:
            # Count occurrences (simple term frequency)
            count = text_lower.count(word)
            score += count
            # logger.debug(f"Density calc: Word '{word}' found {count} times.")
        
        # Normalize by number of significant words in title
        density = score / len(words)
        logger.debug(f"Title density for '{title}': {density:.2f} (score={score}, words={len(words)}, significant_words={words})")
        return density

    @staticmethod
    def extract_title_candidate(text: str, max_lines_search: int = 20) -> str:
        """!
        @brief Heuristically identifies the most likely job title from the text.
        
        @details
        Algorithm:
        1. Single Pass Scan:
           - Checks Top 20 lines for Heuristic Candidates.
           - Checks Bottom 20 lines for Heuristic Candidates.
           - Checks ALL lines for Explicit Candidates ("Role:", "Job Title:").
        2. Conflict Resolution: Density Check.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            logger.debug("Empty text provided for title extraction.")
            return ""

        total_lines = len(lines)
        logger.debug(f"Starting title extraction. Total lines: {total_lines}")
        
        # Candidates
        explicit_candidate = ""
        best_heuristic_line = lines[0]
        best_heuristic_score = -1.0

        role_indicators = SeniorityAnalyzer.get_role_indicators()
        prefixes = ["role:", "job title:", "title:", "position:"]

        # --- Single Pass Loop ---
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 1. Explicit Check (Run on EVERY line)
            if not explicit_candidate: # Stop looking if we found one (first match priority)
                for prefix in prefixes:
                    if line_lower.startswith(prefix):
                        candidate = line[len(prefix):].strip()
                        logger.debug(f"Checking explicit prefix match on line {i}: '{line}' -> Candidate: '{candidate}'")
                        
                        # Allow 2+ words (e.g. "Web Designer")
                        words = candidate.split()
                        if 1 < len(words) < 10:
                            explicit_candidate = candidate
                            logger.info(f"Found explicit title candidate: '{explicit_candidate}'")
                            break
                        else:
                            logger.debug(f"Explicit candidate rejected due to length: {len(words)} words.")
            
            # 2. Heuristic Check (Run only on Top 20 OR Bottom 20)
            is_top = i < max_lines_search
            is_bottom = i >= (total_lines - max_lines_search)
            
            if is_top or is_bottom:
                words_in_line = line.split()
                word_count = len(words_in_line)
                
                # Filter by word count
                if 2 <= word_count <= 8:
                    # Calculate Score
                    
                    # Position Score: 
                    # Top lines get high score (1.0 down to ~0.05)
                    # Bottom lines get medium score (constant 0.5 to prioritize them over random middle text)
                    if is_top:
                        position_score = 1.0 / (i + 1)
                    else:
                        position_score = 0.5 

                    # Keyword Score
                    keyword_matches = 0
                    for indicator in role_indicators:
                        if indicator in line_lower:
                            keyword_matches = keyword_matches + 1
                    
                    current_score = position_score + (keyword_matches * 2.0)
                    
                    # logger.debug(f"Heuristic Check Line {i}: '{line}' | PosScore: {position_score:.2f} | Matches: {keyword_matches} | Total: {current_score:.2f}")

                    if current_score > best_heuristic_score:
                        best_heuristic_score = current_score
                        best_heuristic_line = line
                        logger.debug(f"New Best Heuristic Candidate: '{best_heuristic_line}' (Score: {best_heuristic_score:.2f})")

        logger.debug(f"Final Best heuristic line candidate: '{best_heuristic_line}' (score={best_heuristic_score:.2f})")

        # 3. Regex Phrase Scanning (Fallback for embedded titles)
        regex_candidate = ""
        indicators_pattern = "|".join([re.escape(k) for k in role_indicators if len(k) > 2])
        
        # Expanded seniority pattern from seniority_keywords.json
        # Use the public getter method instead of accessing protected member
        seniority_keywords = SeniorityAnalyzer.get_title_keywords()
        seniority_pattern = "|".join([re.escape(k) for k in seniority_keywords])
        
        # Updated regex to capture numeric/Roman numeral suffixes (e.g. "Software Engineer III", "Engineer-4", "Engineer : 2")
        # (?:\s*[-:]?\s*) -> Matches optional separator (space, hyphen, colon) with optional spaces around it
        phrase_pattern = rf"\b({seniority_pattern})\s+[\w\s]{{0,20}}\b({indicators_pattern})(?:\s*[-:]?\s*)(?:I{{1,3}}|IV|V|VI|[1-9])?\b"
        
        match = re.search(phrase_pattern, text[:2000], re.IGNORECASE)
        if match:
            regex_candidate = match.group(0) # Use group 0 to get the full match
            logger.debug(f"Found regex title candidate: '{regex_candidate}'")
        else:
            logger.debug("No regex title candidate found.")

        # Select best Heuristic
        heuristic_candidate = best_heuristic_line
        if regex_candidate:
            heuristic_candidate = regex_candidate
            logger.debug(f"Using Regex candidate '{regex_candidate}' as the primary Heuristic Candidate.")

        # 4. Conflict Resolution
        if explicit_candidate:
            logger.debug(f"Conflict Resolution: Explicit '{explicit_candidate}' vs Heuristic '{heuristic_candidate}'")

            # If heuristics didn't find ANY role keywords in the candidate, Explicit automatically wins
            h_lower = heuristic_candidate.lower()
            e_lower = explicit_candidate.lower()
            
            # Check if the heuristic candidate contains any role keywords
            has_role_kw = False
            for keyword in role_indicators:
                if keyword in h_lower:
                    has_role_kw = True
                    break
            
            if not has_role_kw:
                 logger.debug(f"Explicit candidate '{explicit_candidate}' wins (no role keywords in heuristic).")
                 return explicit_candidate

            # --- Specificity Check (Superset Logic) ---
            # If Heuristic contains Explicit (e.g. "Data Scientist III" contains "Data Scientist")
            # AND Heuristic is not ridiculously long, prefer Heuristic.
            if e_lower in h_lower and len(h_lower) < len(e_lower) + 10:
                 logger.debug(f"Heuristic candidate '{heuristic_candidate}' wins (More specific superset of '{explicit_candidate}').")
                 return heuristic_candidate

            explicit_density = TextProcessor._calculate_title_density(explicit_candidate, text)
            heuristic_density = TextProcessor._calculate_title_density(heuristic_candidate, text)
            
            if heuristic_density > explicit_density:
                logger.debug(f"Heuristic candidate '{heuristic_candidate}' wins by density ({heuristic_density:.2f} > {explicit_density:.2f}).")
                return heuristic_candidate
            else:
                logger.debug(f"Explicit candidate '{explicit_candidate}' wins by density ({explicit_density:.2f} >= {heuristic_density:.2f}).")
                return explicit_candidate

        logger.debug(f"Returning heuristic candidate: '{heuristic_candidate}'")
        return heuristic_candidate

    @staticmethod
    def clean_text(text: str) -> str:
        """!
        @brief Normalizes and sanitizes input text for processing.
        """
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE) 
        text = re.sub(r'\s+', ' ', text) 
        return text

    @staticmethod
    def extract_skills(text: str, sorted_terms: List[str], alias_map: Dict[str, str]) -> List[str]:
        """!
        @brief Scans text for known skills (Canonicals AND Aliases) using Greedy Longest-Match + Masking.
        """
        found_ids: Set[str] = set()
        work_text: str = TextProcessor.clean_text(text)
        
        # logger.debug(f"Extracting skills from text (length={len(text)})...")
        
        for term in sorted_terms:
            if term not in work_text:
                continue
                
            pattern = r'(?<!\w)' + re.escape(term) + r'(?!\w)'
            
            if re.search(pattern, work_text):
                if term in alias_map:
                    canonical = alias_map[term]
                    found_ids.add(canonical)
                    # logger.debug(f"Found skill: '{term}' -> '{canonical}'")
                work_text = re.sub(pattern, ' @@@ ', work_text)
        
        # logger.debug(f"Total unique skills found: {len(found_ids)}")
        return list(found_ids)
