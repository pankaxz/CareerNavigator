import sys
import os
import re

# Add parent directory to path to allow importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_processor import TextProcessor

def parse_raw_jds(file_path, limit=10):
    """Parses raw_jds.txt to extract role titles and descriptions."""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return []

    with open(file_path, 'r') as f:
        content = f.read()
    
    jds = []
    blocks = content.split('###END###')
    for block in blocks:
        if not block.strip():
            continue
            
        # Try to find title using common patterns in raw_jds.txt
        # Pattern 1: Role: X
        # Pattern 2: Project Role :X
        title_match = re.search(r'(?:Project Role\s*:|Role\s*:)\s*(.*)', block, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Unknown Role"
        
        # We use the whole block as description for comprehensive scoring
        jds.append({"title": title, "desc": block.strip()})
        
        if len(jds) >= limit:
            break
            
    return jds

def test_seniority():
    # 1. Hardcoded Test Cases (Baseline)
    print("Running Baseline Test Cases...")
    print("=" * 40)
    baseline_cases = [
        {
            "title": "Junior Software Engineer",
            "desc": "Help us develop features, fix bugs, and learn from our team. Assist in documentation and support existing systems.",
            "expected_level": "Junior"
        },
        {
            "title": "Software Engineer",
            "desc": "Implement new features, write clean code, and debug issues. 3 years of experience required. Knowledge of Python and SQL.",
            "expected_level": "Mid"
        },
        {
            "title": "Senior Backend Architect",
            "desc": "Lead the design of our distributed systems. 8 years of experience. Mentor junior engineers and define the technical vision. Optimize for high availability and scalability.",
            "expected_level": "Senior"
        }
    ]

    for i, case in enumerate(baseline_cases):
        result = TextProcessor.detect_seniority(case["title"], case["desc"])
        print(f"Baseline {i+1}: {case['title']}")
        print(f"  Result: Score={result['score']}, Level={result['level']}")
        assert result["level"] == case["expected_level"]
        print("  Status: PASSED")
        print("-" * 30)

    # 2. Batch Test from raw_jds.txt
    print("\nRunning Batch Test from raw_jds.txt...")
    print("=" * 40)
    raw_file = os.path.join(os.path.dirname(__file__), '..', 'raw_jds.txt')
    raw_jds = parse_raw_jds(raw_file, limit=10)

    for i, jd in enumerate(raw_jds):
        result = TextProcessor.detect_seniority(jd["title"], jd["desc"])
        print(f"Batch JD {i+1}: {jd['title']}")
        print(f"  Score: {result['score']}")
        print(f"  Level: {result['level']}")
        
        # Print a short snippet of the JD to correlate with the score
        snippet = jd["desc"][:150].replace('\n', ' ')
        print(f"  Snippet: {snippet}...")
        
        # Check if "senior" is in title but level is Junior/Mid (just a sanity warning)
        if "senior" in jd["title"].lower() and result["level"] != "Senior":
            print(f"  [!] Warning: Title is Senior but detected level is {result['level']}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_seniority()

