# CareerNavigator Core - Simple Documentation

This document explains the entire codebase in the simplest way possible.

---

## 1. Program.cs
**Purpose:** The entry point of the application. It sets up the web server and registers services.

**Pseudo Code:**
```
Create WebApplication Builder
Register UniverseProvider as Singleton (One instance forever)
Register SkillScanner as Scoped (One instance per request)
Add Controllers
Configure CORS (Allow "NavGui" to access API)
Build App
Use CORS
Map Controllers (Connect URLs to code)
Add default "/" route (Hello message)
Run App
```

---

## 2. Models (Data Structures)

### Models/Schema/Node.cs
**Purpose:** Represents a single "Skill" or "Star" in the universe.
**Data Structure:** Class (Object)
**Fields:**
- `Id` (String): Unique name (e.g., "python")
- `Group` (String): Category (e.g., "Languages")
- `Val` (Int): Size/Importance
- `SeniorityScore` (Double): 0.0 to 1.0
- `IsSenior` (Bool): True/False

### Models/Schema/Link.cs
**Purpose:** Represents a connection between two skills.
**Data Structure:** Class (Object)
**Fields:**
- `source` (String): Start skill ID
- `target` (String): End skill ID
- `value` (Int): Connection strength

### Models/Schema/Universe.cs
**Purpose:** The container for the entire graph.
**Data Structure:** Class (Object)
**Fields:**
- `Nodes` (List<Node>): All skills
- `Links` (List<Link>): All connections

### Models/DTOs/AnalysisRequest.cs
**Purpose:** Data Transfer Object for receiving Job Description (JD) text.
**Data Structure:** Class (Object)
**Fields:**
- `Text` (String): The raw JD text

---

## 3. Engines (Logic)

### Engines/UniverseProvider.cs
**Purpose:** Loads the `universe.json` file into memory once at startup.
**Algorithm:** File I/O + JSON Deserialization
**Time Complexity:** O(N) where N is file size (only runs once).
**Pseudo Code:**
```
Constructor:
  Path = "Data/universe.json"
  If file exists:
    Read all text
    Deserialize JSON to Universe object
  Else:
    Create empty Universe
  Store Universe in memory

Method GetUniverse():
  Return stored Universe
```

### Engines/SkillScanner.cs
**Purpose:** Scans text to find known skills.
**Algorithm:** Linear Search with Regex Matching
**Time Complexity:** O(S * T) where S is number of skills and T is text length.
**Pseudo Code:**
```
Method FindMatches(text):
  If text is empty, return empty list
  Get all Skill IDs from UniverseProvider
  Convert text to lowercase
  
  For each Skill ID:
    Create Regex Pattern: "\b" + skill_id + "\b" (Whole word match)
    If Regex matches text:
      Add Skill ID to results
      
  Return results
```

---

## 4. Controllers (API Endpoints)

### Controllers/MapController.cs
**Purpose:** Serves the graph data to the frontend.
**Endpoint:** `GET /api/map/universe`
**Pseudo Code:**
```
Method GetUniverse():
  Call UniverseProvider.GetUniverse()
  Return HTTP 200 (OK) with the Universe object
```

### Controllers/NavigatorController.cs
**Purpose:** Analyzes Job Descriptions (JDs).
**Endpoint:** `POST /api/navigator/analyze`
**Pseudo Code:**
```
Method Analyze(request):
  If request.Text is empty:
    Return HTTP 400 (Bad Request)
    
  Call SkillScanner.FindMatches(request.Text)
  Return HTTP 200 (OK) with list of found skills
```