# ML-Driven Educational Data Integrity Auditing System

An enterprise-grade Python automated verification platform designed for massive educational datasets. It uses advanced Machine Learning, semantic embeddings, and a specialized Cybersecurity educational taxonomy to validate dataset integrity against the open web.

## Key Features

- **No Paid API Dependency**: Employs local ML models (`sentence-transformers`, `XGBoost`) instead of paid LLMs.
- **Taxonomy Support**: Natively understands Foundation, Network, System, Application, Forensics, and Ethical Security domains and provides auto-correction suggestions.
- **Deep Feature Engineering**: Generates text similarities, boolean flags, numeric differences, and ranking disparities.
- **Supervised Integrity Classifier**: Categorizes the integrity as `VALID`, `PARTIAL_MATCH`, `OUTDATED`, `INVALID`, `BROKEN_LINK`, or `MISSING_DATA`.
- **High Performance Crawling**: Uses `Playwright` asynchronously alongside SQLite checkpoint recovery.

## Setup Instructions

1. **Set up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install all Heavy ML & Crawling Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your favorite editor
   ```

## Step 1: Train the ML Model

Before running the audit, you must generate the synthetic dataset and train the underlying XGBoost classification model.

```bash
python -m ml.trainer
```
*This will create the synthetic labeled dataset, train the `verification_model.pkl`, evaluate metrics, and save it to the `models/` folder.*

## Step 2: Run the Auditor

Execute the agent against your educational dataset (Excel, CSV, PDF). The system will automatically scrape the pages concurrently and use the trained ML model for validation.

```bash
python main.py path/to/dataset.csv
```

### Outputs
- **`reports/`**: Final CSV, Excel, and JSON outputs containing taxonomy predictions, similarity scores, and final classifications.
- **`models/metrics.json`**: Confusion matrix, accuracy, precision, and F1 scores from model training.
- **`logs/`**: Checkpoint DB to resume paused crawls.
- **`snapshots/`**: Screenshots of broken pages.
