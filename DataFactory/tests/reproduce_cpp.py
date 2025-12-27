import sys
import os
import re

# Add parent directory to path to allow importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_processor import TextProcessor

def test_cpp_detection():
    text = "We are looking for a strong C++ developer with experience in embedded systems."
    skills = ["c++", "python"]
    
    print(f"Text: '{text}'")
    print(f"Skills to find: {skills}")
    
    found = TextProcessor.extract_skills(text, skills)
    print(f"Found: {found}")
    
    if "c++" not in found:
        print("FAIL: C++ not detected!")
    else:
        print("PASS: C++ detected.")

if __name__ == "__main__":
    test_cpp_detection()
