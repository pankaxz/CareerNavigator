# Career Navigator DataFactory - System Documentation

This file explains the inner workings of the DataFactory engine in the simplest terms possible.

---

## 1. processor.py (The Orchestrator)
**What it does:**  
This is the main script that runs the factory. It acts as a "General Contractor," delegating specific work to the specialized utility classes below. It loads data, calls the builders, and saves the results.

**Key Functions:**
- `process_data()`: The main entry point.

---

## 2. utils/graph_builder.py (The Builder)
**What it does:**  
Manages the construction of the knowledge graph. It handles the raw counting and statistical aggregation.

**Key Functions:**
- `initialize_stats()`: Prepares empty counters.
- `update_metrics()`: Adds a single JD's data to the global graph.
- `prepare_nodes_list()`: Transforms raw counts into the final list of nodes.
- `filter_edges()`: Applies the threshold to connections.

---

## 3. utils/text_processor.py (The Miner / NLP Engine)
**What it does:**  
This is the "Smart" part of the system. It takes raw, messy text and extracts structured data (Skills and Seniority).

**Data Structures Used:**
- **List:** Stores lists of keywords (Action Verbs, Impact Scopes).
- **Strings:** Raw text processing.

**Algorithms Used:**
- **Regex (Regular Expressions):**  
    Regex is used for three critical tasks:
    1. **Data Cleaning**: Stripping URLs (`http\S+`) and collapsing multiple spaces (`\s+`) into one.
    2. **Pattern Matching**: Identifying years of experience (e.g., `(5\+|[5-9])`) across different variations like "5+ years", "8 yrs", or "10 year".
    3. **Precise Skill Extraction**: Using "Word Boundaries" (`\b`).
        - Without `\b`, searching for "Go" would incorrectly match "Google" or "Django".
        - `\b` acts like a "textual anchor" that only triggers a match if the character before and after the word is not a letter/number (e.g., a space or punctuation).
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
    - Threshold Filtering mechanism:

    Threshold: Set to 3. This means a skill must appear in at least 3 Job Descriptions to be included in the 
    universe.json
     output.
    Filtering Logic:
    Nodes: Only skills with total count >= 3 are added.
    Edges: Only links between two valid (filtered) nodes with co-occurrence count >= 3 are added.
    Seniority Scores: The system now calculates and includes seniorityScore and isSenior status for every node in the output.
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
      - id (string): The unique identifier for the skill (e.g., "python", "kubernetes"). This matches the exact string found in the text processing stage.
      - group (string): The category to which the skill belongs (e.g., "Languages", "Frameworks"). This is used for styling and filtering in the frontend.
      - val (number): The total count of occurrences of the skill across all Job Descriptions. This is used for sizing the node in the frontend.
      - seniorityScore (number): The ratio of "Senior" occurrences vs. total occurrences. This is used for coloring the node in the frontend.
      - isSenior (boolean): True if the seniorityScore is > 0.6. This is used for filtering in the frontend.
  
    - `links`: The lines connecting them (Co-occurrences).
      - source (string): The id of the starting node.
      - target (string): The id of the ending node.
      - value (int): The strength of the connection. It represents the number of JDs where both skills appeared together. In the visualization, this determines the thickness or pull of the line connecting the stars.
      - seniorityScore (number): The ratio of "Senior" occurrences vs. total occurrences. This is used for coloring the node in the frontend.
      - isSenior (boolean): True if the seniorityScore is > 0.6. This is used for filtering in the frontend.
