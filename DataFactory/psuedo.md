# Career Navigator DataFactory - System Documentation

This file explains the inner workings of the DataFactory engine in the simplest terms possible.

---

## 1. processor.py (The Orchestrator)
**What it does:**  
This is the main script that runs the factory. It iterates through all the loaded Job Descriptions (JDs), uses the other utilities to extract data, and aggregates the results into a massive graph.

**Data Structures Used:**
- **Dictionary (Hash Map):** `node_stats` maps every skill to its statistics (Total Count, Senior Count). Fast lookups O(1).
- **Dictionary:** `edge_counts` maps a pair of skills `("React", "Next.js")` to their connection frequency.
- **Set:** Used implicitly to store unique skills found in a single JD.

**Algorithms Used:**
- **Nested Loops:** 
    1. Loop through every JD.
    2. Loop through every skill found in that JD.
- **Combinations:** Uses `itertools.combinations(skills, 2)` to create every possible pair of skills (nodes) to form links (edges). If a JD has 5 skills, it creates 10 links.
- **Aggregation:** Sums up counts as it goes.

---

## 2. utils/text_processor.py (The Miner / NLP Engine)
**What it does:**  
This is the "Smart" part of the system. It takes raw, messy text and extracts structured data (Skills and Seniority).

**Data Structures Used:**
- **List:** Stores lists of keywords (Action Verbs, Impact Scopes).
- **Strings:** Raw text processing.

**Algorithms Used:**
- **Regex (Regular Expressions):**  
    - `r'\b' + skill + r'\b'` ensures we match "Go" (the language) but ignore "Google".
    - `(5\+|[5-9])` matches specific years of experience patterns.
- **Heuristic Scoring (Weighted Sum):**  
    - Iterates through the text checking for "signals".
    - Assigns points: Title (+3), Years (+3), Keywords (+1).
    - Thresholding: If `Score >= 6`, classifying as "Senior".

---

## 3. utils/io_handler.py (The Logistics Manager)
**What it does:**  
Handles all File Input and Output. It ensures the data leaving the system is cleaner than the data entering it.

**Data Structures Used:**
- **JSON Object:** The final structure for `universe.json`.
- **Lists of Dictionaries:** Used to prepare rows for CSV writing.

**Algorithms Used:**
- **Normalization:** Converts the internal dictionary data into the strict JSON schema required by the Frontend graph library.
- **Seniority Calculation:** 
    - `Score = Senior_Count / Total_Count`.
    - `IsSenior = Score > 0.6`.

---

## 4. output/taxonomy.py (The Map)
**What it does:**  
The configuration file. It defines the "World" we are looking for. If a skill isn't here, the system doesn't see it.

**Data Structures Used:**
- **Dictionary:** Maps `Category Name` -> `List of Skills`.
- **List:** A flat list of strings for each category.

---

## 5. raw_jds.txt (The Raw Material)
**What it does:**  
The source fuel. Contains hundreds of raw Job Descriptions pasted from LinkedIn/Glassdoor.

**Separators:**
- Uses `###END###` as a delimiter to separate different JDs so the `processor.py` knows where one ends and the next begins.

---

## 6. output/universe.json (The Final Product)
**What it does:**  
The database for the frontend.

**Data Structures Used:**
- **Graph (Network):**
    - `nodes`: The dots (Skills).
    - `links`: The lines connecting them (Co-occurrences).
