# CareerNavigator DataFactory Documentation {#mainpage}

## 🚀 Overview

The **DataFactory** is the high-performance Extract-Transform-Load (ETL) pipeline for CareerNavigator. Its primary responsibility is to ingest unstructured text (Job Descriptions), analyze them using Natural Language Processing (NLP) heuristics, and construct a semantic knowledge graph (The **Universe**).

This graph serves as the foundational data layer for the Core Backend, enabling features like:
- Skill Gap Analysis
- Role Seniority Classification
- Career Path Recommendations

---

## 🏗 Architecture

The pipeline follows a strict linear flow, optimized for determinism and reproducibility.

```mermaid
graph TD
    A[Raw JDs (Text)] -->|IOHandler| B(Processor Orchestrator)
    B --> C{Analyzer Loop}
    C -->|TextProcessor| D[Skill Extraction]
    C -->|TextProcessor| E[Seniority Scoring]
    D --> F[GraphBuilder Accumulator]
    E --> F
    F -->|Thresholding| G[Analytics Engine]
    G -->|Normalization| H[Output Generation]
    H -->|JSON| I[Universe.json]
    H -->|CSV| J[Cosmograph Visuals]
```

## 🧠 Core Logic: Seniority Scoring

One of the most complex components is the `TextProcessor::detect_seniority` algorithm. It uses a weighted heuristic model to assign a seniority level to every job description.

### Scoring Matrix

| Category | Weight Breakdown | Max Score |
| :--- | :--- | :--- |
| **Title** | Managerial Words (+5.0), Senior Words (+4.0) | **5.0** |
| **Experience** | 5+ Years (+5.0), 3-4 Years (+2.5) | **5.0** |
| **Action Verbs** | Words like "Architect", "Orchestrate" (Count * 0.4) | **2.0** |
| **Scope** | "Distributed Systems", "Scalability" (Count * 0.5) | **1.5** |
| **Leadership** | "Mentoring", "Hiring" (Count * 0.5) | **1.5** |
| **paradigms** | "Event-Driven", "Cloud-Native" (Count * 0.5) | **1.0** |
| **NFRs** | "Security", "Observability" (Count * 0.5) | **1.0** |

### Classification Thresholds

- **Managerial**: Explicit "Manager" title OR Score (implied, though currently title-driven).
- **Senior**: Score &ge; 9.0
- **Mid**: Score &ge; 5.0
- **Junior**: Score < 5.0

---

## 📂 Output Formats

### 1. `universe.json` (Application Data)
The canonical graph representation used by the C# Backend (`UniverseProvider`).

```json
{
  "nodes": [
    { "id": "python", "group": "Languages", "seniorityScore": 0.45, "managerialScore": 0.1 }
  ],
  "links": [
    { "source": "python", "target": "docker", "value": 150, "isSenior": true }
  ]
}
```

### 2. Cosmograph CSVs (Visualization)
Optimized flat files for rendering in [Cosmograph](https://cosmograph.app).
- `nodes.csv`: ID, Group, Weight
- `edges.csv`: Source, Target, Weight

---

## 🔧 Usage

Run the pipeline from the `CareerNavigator` root:

```bash
python3 DataFactory/processor.py
```
