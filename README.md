# ML-Driven Educational Data Integrity Auditing System

An enterprise-grade Python automated verification platform designed for massive educational datasets. It uses advanced Machine Learning, semantic embeddings, and a specialized Cybersecurity educational taxonomy to validate dataset integrity against the open web.

## Prerequisites

- **Python**: 3.8 or higher.
- **pip**: Python package manager.
- **Chromium Browser**: Installed via Playwright for web scraping.
- **Ollama**: (Optional) Running locally with `llama3.2` for structured LLM fallback verification.

## Key Features

- **Dynamic Streamlit Dashboard**: A professional interactive dashboard (`streamlit run dashboard/app.py`) to visualize auditing statistics, KPI metrics, status distributions, and inspect detailed course records (with corrections and error screenshots).
- **Hybrid Verification Pipeline**: Utilizes local ML models (`sentence-transformers`, `XGBoost`) for fast classifications and automatically falls back to a local LLM (`llama3.2` via Ollama) when the ML confidence score is below 80%.
- **Deep Context Crawling**: Scraping now crawls up to 2 related internal pages (e.g. syllabus, program, about, details) to compile a rich, comprehensive textual context of the course before verification.
- **Beautiful Enterprise Reports**: Saves custom-tailored reports (`reports/`) containing specific field checks (Institute, Mode, Country, Skills). The Excel sheet comes with styled headers, text wrapping, frozen rows, and status-based cell coloring (Green = Valid, Yellow = Partial, Light Red = Invalid, Dark Red = Broken).
- **Playwright Anti-Detection**: Uses randomized Chrome user agents and request headers to bypass common bot protection/WAF blocks.
- **Specialized PDF Vision Parser**: Integrates visual span sorting (top-to-bottom, left-to-right) for robust reading of grid layouts, and splits course headers intelligently into course names and institute names.

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
   # Edit .env to set your parameters (Optional: configure local Ollama endpoint)
   ```

## Configuration

The system is configured using a `.env` file at the root level. Supported environment variables include:

- `OPENAI_API_KEY`: API key for optional AI Verification Engine features. Defaults to a placeholder. If using Ollama, set this to `ollama`.
- `DEFAULT_LLM_MODEL`: Specifies the LLM model to use (default is `google/gemma-4-31b-it` or `llama3.2` for local Ollama).
- `CONCURRENCY_LIMIT`: Number of concurrent web scrapes allowed (default is 5).
- `TIMEOUT_SECONDS`: Global timeout parameter for requests (default is 30).
- `RETRIES`: Number of retry attempts on failure (default is 3).
- `EMBEDDING_MODEL_NAME`: Specifies the local sentence embedding model (default is `all-MiniLM-L6-v2`).

## Local LLMs via Ollama Support

If you want to use local LLMs (like `llama3.2`) through Ollama instead of OpenAI, the AI engine is preconfigured to connect to your local Ollama endpoint (usually `http://localhost:11434/v1`).
1. Make sure you have Ollama running locally.
2. Pull the model:
   ```bash
   ollama pull llama3.2
   ```
3. Run the auditor as usual, and it will handle Ollama fallbacks automatically.

## Supported Input Formats

The auditing system can ingest datasets in multiple formats:
- **CSV**: Comma-separated values (e.g., `dataset.csv`).
- **Excel**: Standard Excel format (e.g., `dataset.xlsx`).
- **PDF**: tabular course records extracted from PDFs (e.g., `dataset.pdf`).

## Usage Workflow

### Step 1: Train the ML Model

Before running the audit, you must generate the synthetic dataset and train the underlying XGBoost classification model.

```bash
python -m ml.trainer
```
*This will create the synthetic labeled dataset, train the `verification_model.pkl`, evaluate metrics, and save it to the `models/` folder.*

### Step 2: Run the Auditor

Execute the agent against your educational dataset (Excel, CSV, PDF). The system will automatically scrape the pages concurrently and use the trained ML model + Ollama fallbacks for validation.

```bash
python main.py path/to/dataset.pdf
```

### Step 3: Launch the Audit Dashboard

Visualize anomalies, audit statistics, and detailed field mismatch reports via the web dashboard.

```bash
streamlit run dashboard/app.py
```

## Project Structure

A high-level overview of the codebase architecture:

- **`ai_engine/`**: Handles the Ollama local LLM comparison between the structured dataset record and the webpage text.
- **`crawler/`**: Responsible for scraping and validating web URLs concurrently using `Playwright` and `aiohttp`.
- **`dashboard/`**: Contains the Streamlit dashboard for audit reports analytics.
- **`extractor/`**: Normalizes and extracts key features from raw HTML data.
- **`ml/`**: Encompasses training logic, synthetic dataset generation, embeddings generation, and integrity classification using `XGBoost`.
- **`parser/`**: Facilitates the parsing of input files, supporting Spreadsheets and PDFs.
- **`reports/`**: Generates and structures final audit output reports (JSON, CSV, Excel formats).
- **`taxonomy/`**: Manages the domain mapping definitions and specialized educational taxonomy.
- **`utils/`**: Shared utilities (schemas, configurations, SQLite checkpointing, logging).
- **`verifier/`**: Contains core logic for integrity checking, duplicate detection, rule-based verification, and calling models.

### Outputs
- **`reports/`**: Final CSV, Excel, and JSON outputs containing taxonomy predictions, similarity scores, custom column sequences, and status colors.
- **`models/metrics.json`**: Confusion matrix, accuracy, precision, and F1 scores from model training.
- **`logs/`**: Checkpoint DB to resume paused crawls.
- **`snapshots/`**: Screenshots of broken pages.
