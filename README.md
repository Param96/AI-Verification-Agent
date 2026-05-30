# ML-Driven Educational Data Integrity Auditing System

An enterprise-grade Python automated verification platform designed for massive educational datasets. It uses advanced Machine Learning, semantic embeddings, and a specialized Cybersecurity educational taxonomy to validate dataset integrity against the open web.

## Prerequisites

- **Python**: 3.8 or higher.
- **pip**: Python package manager.
- **Chromium Browser**: Installed via Playwright for web scraping.

## Key Features

- **No Paid API Dependency**: Employs local ML models (`sentence-transformers`, `XGBoost`) instead of paid LLMs. (Optional AI features via OpenAI or Ollama are supported).
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

## Configuration

The system can be configured using a `.env` file at the root level. Supported environment variables include:

- `OPENAI_API_KEY`: API key for optional AI Verification Engine features. If using an OpenAI-compatible local API (e.g., Ollama), you can place any dummy key here.
- `CONCURRENCY_LIMIT`: Number of concurrent web scrapes allowed (default is 5).
- `TIMEOUT_SECONDS`: Global timeout parameter for requests (default is 30).
- `RETRIES`: Number of retry attempts on failure (default is 3).
- `DEFAULT_LLM_MODEL`: Specifies the LLM model to use (default is `gpt-4o-mini`). When using Ollama, you can set this to `llama3.2` or any other supported local model.
- `EMBEDDING_MODEL_NAME`: Specifies the local sentence embedding model (default is `all-MiniLM-L6-v2`).

## Local LLMs via Ollama Support

If you want to use local LLMs (like `llama3.2`) through Ollama instead of OpenAI, the AI engine can be adapted to connect to your local Ollama endpoint (usually `http://localhost:11434/v1`).
- Set `DEFAULT_LLM_MODEL=llama3.2` (or your preferred local model) in `.env`.
- Ensure the `OPENAI_API_KEY` in `.env` is set to any dummy string (e.g., `ollama`).
- Set up the OpenAI client base URL pointing to the Ollama API endpoint in the AI verification engine setup.

## Supported Input Formats

The auditing system can ingest datasets in multiple formats:
- **CSV**: Comma-separated values (e.g., `dataset.csv`).
- **Excel**: Standard Excel format (e.g., `dataset.xlsx`).
- **PDF**: Extracts course records tabular data from PDFs (e.g., `dataset.pdf`).

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

## Project Structure

A high-level overview of the codebase architecture:

- **`ai_engine/`**: Handles the optional LLM-based (OpenAI or Ollama) comparison between the structured dataset record and the extracted webpage text.
- **`crawler/`**: Responsible for scraping and validating web URLs concurrently using `Playwright` and `aiohttp`.
- **`extractor/`**: Normalizes and extracts key features from raw HTML data.
- **`ml/`**: Encompasses training logic, synthetic dataset generation, embeddings generation, and integrity classification using `XGBoost`.
- **`parser/`**: Facilitates the parsing of input files, supporting Spreadsheets and PDFs.
- **`reports/`**: Generates and structures final audit output reports (JSON, CSV, Excel formats).
- **`taxonomy/`**: Manages the domain mapping definitions and specialized educational taxonomy.
- **`utils/`**: Shared utilities (schemas, configurations, SQLite checkpointing, logging).
- **`verifier/`**: Contains core logic for integrity checking, duplicate detection, rule-based verification, and calling models.

### Outputs
- **`reports/`**: Final CSV, Excel, and JSON outputs containing taxonomy predictions, similarity scores, and final classifications.
- **`models/metrics.json`**: Confusion matrix, accuracy, precision, and F1 scores from model training.
- **`logs/`**: Checkpoint DB to resume paused crawls.
- **`snapshots/`**: Screenshots of broken pages.
