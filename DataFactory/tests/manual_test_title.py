
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.text_processor import TextProcessor
from utils.seniority_analyzer import SeniorityAnalyzer

def test_title_extraction():
    jd_text = """Meet the team:

The Firmware team is responsible for designing and implementation of wearable and handheld receiver firmware and embedded software at Dexcom. This includes from early research through to product manufacturing. The FW team is embarking on transformational improvements in deploying best in class agile methodologies, AI implementations, Telemetry Data Analysis, and new build frameworks. The Staff Firmware Engineer will work closely with Electrical Engineering, Systems Engineering, V&V test team, and SW development teams.


Where you come in:

You will bring expertise in bare metal firmware and embedded RTOS software design & development.
You will lead projects as a System Integrator for the Embedded Firmware team, managing the Sprints, Schedule, and Resource Skill Set alignment.
You will have in-depth experience with software development tools (e.g., Jira, Github, Make).
You will be called on to support other departments to resolve product complaints, IOP triage or when expert advice is needed.
You will be expected to be collaborative, open, transparent, and team-oriented with a focus on team empowerment with shared responsibility and flexibility.
You will ensure delivery of technology and product development cycles on-time, on budget and with high quality results.

What makes you successful:

You bring a breath of experience in high-reliability firmware design, including agile development values & principals.
You have experience leading a Embedded Firmware team for project execution.
You bring experience including the full firmware development life cycle which includes requirements, design, coding, testing and integration of low power systems.
You bring experience in hands-on embedded systems with a fast-paced complex product development process where power management, signal processing, BLE/Wifi connectivity, memory allocation, and complex algorithms are key product design elements.
You will have 5+ years of experience at bare metal C/C++ programming for embedded ARM microcontrollers; including use of Make and GCC cross compilers.
You have previously worked with CI/CD pipeline frameworks, scrums/kanban, branching strategies, and utilization of latest developmental tools.
You have experience in creating and maintaining software requirements and the development of test use cases from the requirements.
You are highly collaborative and have a desire to reach across the organization to understand stakeholder needs and how to meet them.
You have a culture of listening, serving with integrity, thinking big, and being dependable.
You have a minimum of a BS degree in either electrical engineering or computer science.

Education and Experience Requirement:

Typically requires a Bachelors degree in a technical discipline, and a minimum of 8-13 years related experience
Role: Automation Test Engineer
Industry Type: Medical Devices & Equipment
Department: Engineering - Software & QA
Employment Type: Full Time, Permanent
Role Category: Quality Assurance and Testing
Education
UG: B.Tech/B.E. in Any Specialization
PG: M.Tech in Any Specialization, MCA in Any Specialization, MS/M.Sc(Science) in Any Specialization"""

    print("--- JD Text (First 10 lines) ---")
    lines = [l.strip() for l in jd_text.split('\n') if l.strip()]
    for i, l in enumerate(lines[:10]):
        print(f"{i}: {l[:60]}...")
    print("-------------------------------\n")
    
    # 1. Standard Extraction
    print("Running extract_title_candidate (default params)...")
    title = TextProcessor.extract_title_candidate(jd_text)
    print(f"✅ Extracted Title Candidate: '{title}'")
    
    # Debug Analysis
    print("\n--- Detailed Scoring Analysis ---")
    role_indicators = SeniorityAnalyzer.get_role_indicators()
    
    for i, line in enumerate(lines[:15]): # Check first 15 lines
        words = line.split()
        wc = len(words)
        line_lower = line.lower()
        
        has_kw = any(k in line_lower for k in role_indicators)
        valid = 2 <= wc <= 8
        
        score = 0.0
        if valid:
            score = 1.0 / (i + 1)
            if has_kw:
                score += 2.0
                
        print(f"Line {i} (Words={wc}): '{line[:40]}...'")
        print(f"   -> Valid: {valid}, HasKeyword: {has_kw} ('{list(k for k in role_indicators if k in line_lower)}'), Score: {score:.4f}")

    # Check for the explicit "Role:" pattern at the end
    print("\n--- Searching for Explicit 'Role:' Pattern ---")
    role_line = next((l for l in lines if l.lower().startswith("role:")), None)
    print(f"Explicit Role Line Found: '{role_line}'")

    if "Automation Test Engineer" in title:
        print("❌ FAILED: Picked 'Automation Test Engineer' (Explicit) over 'Firmware Engineer' (Heuristic)")
    elif "Firmware" in title:
        print("✅ SUCCESS: Picked 'Firmware Engineer' (Heuristic) due to higher density.")
    else:
        print(f"❓ UNKNOWN: Picked '{title}'")

if __name__ == "__main__":
    test_title_extraction()
