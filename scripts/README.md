# Scripts Directory

This directory contains utility scripts for the Verityn AI project.

## Scripts

- `generate_test_data.py` - Generate synthetic test documents for development
- `classification_training.py` - Train and evaluate document classification models
- `ragas_evaluation.py` - Run RAGAS evaluation on chat responses
- `performance_analysis.py` - Analyze system performance metrics

## Usage

Run scripts from the project root directory:

```bash
# Generate test data
python scripts/generate_test_data.py

# Train classification model
python scripts/classification_training.py

# Run RAGAS evaluation
python scripts/ragas_evaluation.py

# Analyze performance
python scripts/performance_analysis.py
```

## Dependencies

All scripts require the project dependencies to be installed. Use the virtual environment:

```bash
# Activate virtual environment
source .venv/bin/activate  # or use UV

# Run scripts
python scripts/script_name.py
``` 