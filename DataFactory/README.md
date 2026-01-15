# CareerNavigator DataFactory

The **DataFactory** is a Python pipeline responsible for transforming raw Job Descriptions into a structured Skill Graph (the "Universe").

## Project Structure

- **`src/`**: Source code.
- **`data/`**: Input data (`input/`) and generated artifacts (`output/`).
- **`config/`**: Configuration settings (`settings.yaml`).

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Data Preparation**:
   Ensure your raw data is present:
   - `data/input/raw_jds.txt`
   - `data/input/taxonomy_alias.json`

## Running the Pipeline

To execute the full factory pipeline, run the following command from the project root (`DataFactory/`):

```bash
PYTHONPATH=src python3 -m main
```

### Options
You can modify behavior by editing `config/settings.yaml`:
- **Threshold**: Minimum occurrences for a skill to be included.
- **Paths**: Locations of input/output files.
