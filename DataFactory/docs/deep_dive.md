# DataFactory: Deep Dive Documentation

This document explains the **DataFactory** repository in extremely explicit detail. It covers **what** every file does, **why** it exists, and **how** the logic works step-by-step.

> [!NOTE] 
> **Goal of this System:**  
> To take hundreds of raw, messy Job Descriptions (text) and turn them into a structured "Universe" of skills (Graph) where we can see which skills are related and which are senior/junior.

---

## 1. Visual File Structure

Here is the anatomy of the project folder:

```text
DataFactory/
│
├── processor.py             <-- THE BOSS (Orchestrator). Starts everything.
├── raw_jds.txt              <-- THE INPUT. A giant text file with pasted JDs.
│
├── utils/                   <-- THE WORKERS. Specialized tools.
│   ├── text_processor.py    <-- The Reader (NLP). Finds skills & seniority in text.
│   ├── graph_builder.py     <-- The Architect. Counts and connects skills.
│   ├── io_handler.py        <-- The Mover. Loads files and saves files.
│   ├── taxonomy_manager.py  <-- The Librarian. Helpers for the skill list.
│   └── analytics_engine.py  <-- The Analyst. Calculates distribution stats.
│
└── output/                  <-- THE DESTINATION. Where results go.
    ├── taxonomy.py          <-- The Dictionary. List of all skills we care about.
    ├── universe.json        <-- The Final Product. Data for the Frontend.
    ├── nodes.csv            <-- Raw Data (for Cosmograh/Excel).
    └── edges.csv            <-- Raw Connections (for Cosmograph/Excel).
```

---

## 2. Detailed Logic Breakdown

### Phase 1: Input & Cleaning (The Fuel)
**File:** `raw_jds.txt` and `utils/io_handler.py` -> `load_raw_jds()`

The system needs to ingest raw text and prepare it for processing.

#### 1. Input Source
Instead of a database, we paste Job Descriptions (JDs) into `raw_jds.txt` separated by `###END###`.
- **Reason:** Fastest way to copy-paste from LinkedIn/Glassdoor.
- **Example:**
  ```text
  Software Engineer needed. Skills: Python, AWS.
  ###END###
  Senior Developer. Skills: Java, Kubernetes.
  ###END###
  ```

#### 2. Splitting Logic (IOHandler)
```python
# Pseudo-Code for load_raw_jds()
FUNCTION load_raw_jds(file_path):
    1. READ entire file to a string -> "Software Engineer... ###END### Senior Dev..."
    2. SPLIT string by delimiter -> ["Software Engineer...", "Senior Dev..."]
    3. LOOP through each segment:
       a. STRIP whitespace (remove blank lines before/after text)
       b. IF segment is not empty:
          ADD to list
    4. RETURN list of cleaned JDs
```

#### 3. Text Cleaning Logic (TextProcessor)
**File:** `utils/text_processor.py` -> `clean_text()`
Before searching for skills, we must "sanitize" the text.

```python
# Pseudo-Code for clean_text(text)
FUNCTION clean_text(input_text):
    1. LOWERCASE everything.
       "Python Developer" -> "python developer"
    
    2. REMOVE URLs (Regex: http\S+ | www\S+)
       - Why? A URL like "github.com/c/project" contains "c". 
       - IF we don't remove it, we might think the JD requires "C" language.
       - Logic: Find specific patterns starting with http/www and delete them.
    
    3. NORMALIZE WHITESPACE (Regex: \s+)
       - Why? "Python    Developer" (tabs/multiple spaces) is hard to match.
       - Logic: Replace ALL sequences of space/tab/newline with a SINGLE space.
       "python    \n developer" -> "python developer"
       
    4. RETURN sanitized_text
```

### Phase 2: Configuration (The Map)
**File:** `output/taxonomy.py`

This is our "Dictionary of Truth". If a skill is NOT in this file, the system will ignore it completely.
- **Structure:** A Dictionary key-value pair.
    - `Key`: A category (e.g., "Languages").
    - `Value`: A list of skills (e.g., ["python", "java", "c++"]).
- **Reasoning:** We want to curate the universe. We don't want "Team Player" or "Hard Worker" showing up as technical skills, so we whitelist *only* what we want.

### Phase 3: The Brain (Seniority Scoring)
**File:** `utils/text_processor.py` -> `detect_seniority()`

We classify each JD into **Junior**, **Mid**, or **Senior** based on a weighted point system. We look for "signals" in the text.

#### The Scoring Algorithm (Detailed)

**Start:** `SCORE = 0`

**Step 1: Title Analysis (The strongest signal)**
- **Senior Keywords:** "senior", "lead", "principal", "architect", "manager", "head", "vp", "director".
- **Junior Keywords:** "junior", "entry", "associate", "intern".
- **Logic:**
  ```python
  IF title has "Senior Keyword" -> ADD 3.0 Points
  ELSE IF title has "Junior Keyword" -> ADD 0 Points
  ELSE (Neutral title) -> ADD 1.5 Points (assume Mid-level default)
  ```

**Step 2: Years of Experience (Regex Extraction)**
- **Senior Pattern:** `(5+|[5-9]|1[0-9]) years`
  - Matches: "5+ years", "8 years", "12 years".
  - **Logic:** IF found -> ADD 3.0 Points.
- **Mid Pattern:** `(3|4) years`
  - Matches: "3 years", "4 years".
  - **Logic:** IF found -> ADD 1.5 Points.

**Step 3: Action Verbs ("Vibe Check")**
- We look for words that imply ownership.
- **List:** "architect", "design", "mentor", "scale", "govern", "innovate"...
- **Logic:**
  ```python
  count = number of these words found in text
  points = count * 0.3
  MAX_LIMIT = 1.5 points (So you can't get infinite points just by spamming keywords)
  ADD points to SCORE
  ```

**Step 4: Scope & Leadership**
- **Scope Keywords:** "microservices", "high availability", "distributed systems" (Words implying big complex systems).
  - **Logic:** ADD up to 1.0 Point.
- **Leadership Keywords:** "mentoring", "hiring", "roadmap".
  - **Logic:** ADD up to 0.5 Points.

**Final Decision:**
```python
IF SCORE >= 6.0:
    RETURN "Senior"
ELSE IF SCORE >= 3.0:
    RETURN "Mid"
ELSE:
    RETURN "Junior"
```

### Phase 4: Building the Graph (Counting Logic)
**File:** `utils/graph_builder.py`

This is where we compile the statistics.

#### Logic A: Initialization (Setting up Buckets)
Before processing any JDs, we create "Zero Counters" for every single skill in our taxonomy.
```python
# node_stats structure
{
    "python": { "total": 0, "senior_count": 0 },
    "java":   { "total": 0, "senior_count": 0 },
    ... for all 500+ skills
}
```

#### Logic B: incremental Updates (The Loop)
For **ONE** Job Description that contains `["python", "aws"]` and is rated `Senior`:

**1. Update Nodes (Skills):**
- Locate "python" in `node_stats`.
- `total` becomes 0 -> 1.
- `senior_count` becomes 0 -> 1 (Because JD was Senior).
- Locate "aws" in `node_stats`.
- `total` becomes 0 -> 1.
- `senior_count` becomes 0 -> 1.

**2. Update Edges (Connections):**
- Find all pairs: `("python", "aws")`.
- Check if this pair exists in `edge_counts`. If not, create it.
- `edge_counts[("python", "aws")]["total"]` += 1.
- `edge_counts[("python", "aws")]["senior_count"]` += 1.

*This process repeats for every single JD, slowly building up massive numbers.*

### Phase 5: The Output
**File:** `utils/io_handler.py` -> `save_universe()`

We format the internal math into JSON for the website.
- **Nodes List:**
    ```json
    {
      "id": "python",
      "group": "Languages",
      "val": 50,              // Final Total from Node Stats
      "seniorityScore": 0.8,  // Calculated: senior_count / total (40 / 50 = 0.8)
      "isSenior": true        // Logic: IF seniorityScore > 0.6 THEN true
    }
    ```
- **Links List:**
    ```json
    {
      "source": "python",
      "target": "aws",
      "value": 25             // Final Total from Edge Counts
    }
    ```

---

## Summary of execution flow

1.  **START**: `processor.py` is called.
2.  **LOAD**: `IOHandler` reads `raw_jds.txt` and gives back a list of strings (Logic Phase 1).
3.  **INIT**: `GraphBuilder` creates empty buckets for every skill in the Taxonomy (Logic Phase 4A).
4.  **LOOP**: For every Job Description in the list:
    *   **Analyze**: `TextProcessor` cleans text (Phase 1) and scores seniority (Phase 3).
        *   "I found [Python, AWS, Docker]."
        *   "I calculate this is a SENIOR role (Score 7.5)."
    *   **Update**: `GraphBuilder` increments the counters (Phase 4B).
5.  **FINALIZE**:
    *   **Filter**: Remove skills/connections that didn't meet the count threshold.
    *   **Calculate**: Compute Seniority % for every skill.
6.  **SAVE**: Write `universe.json` to the output folder (Phase 5).
7.  **END**: Print "Done".
