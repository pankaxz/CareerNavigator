import sys
import os

# Add parent directory to path to allow importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_processor import TextProcessor

def test_seniority():
    test_cases = [
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
        },
        {
            "title": "Staff Engineer",
            "desc": "Strategize our long-term roadmap. Drive architectural decisions across microservices. Champion SOLID principles and design patterns. Oversee observability and performance tuning.",
            "expected_level": "Senior"
        }
    ]

    for i, case in enumerate(test_cases):
        result = TextProcessor.detect_seniority(case["title"], case["desc"])
        print(f"Test Case {i+1}: {case['title']}")
        print(f"  Result: Score={result['score']}, Level={result['level']}")
        print(f"  Expected: {case['expected_level']}")
        # Note: Exact score might vary, but level should be correct for these obvious cases.
        assert result["level"] == case["expected_level"] or (result["level"] == "Senior" and case["expected_level"] == "Senior")
        print("  Status: PASSED")
        print("-" * 30)

if __name__ == "__main__":
    test_seniority()
