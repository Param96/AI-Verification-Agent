# Enterprise Verification Platform 🚀

An enterprise-grade, distributed AI auditing platform that automatically verifies information published in massive offline documents (PDFs, spreadsheets, catalogs) against live reality on the internet.

Originally built as a local python script, this project has been fully transformed into a highly scalable **Enterprise Architecture** leveraging microservices, message queues, scalable worker nodes, and a modern frontend dashboard.

## 🏗 System Architecture

The platform operates across three main distributed layers:

### 1. The Real-Time Dashboard (Frontend)
- **Framework**: Built natively in Next.js 15.
- **Aesthetics**: Custom-built Vanilla CSS design system emphasizing Glassmorphism, deep gradients, fluid micro-animations, and an immersive dark mode.
- **Features**: Live progression tracking, granular table data viewers, and deep-dive modals presenting AI LLM reasoning side-by-side with web screenshot evidence.

### 2. The Core API & Infrastructure (Backend)
- **FastAPI Core**: A high-performance async REST API handling web traffic and orchestrating job creation.
- **PostgreSQL**: Robust, relational SQL storage managing multi-tenant `Organizations`, `Users`, `Jobs`, `Records`, and granular AI `Evidence`.
- **MinIO (S3)**: Highly scalable object storage safely caching multi-gigabyte PDF uploads, massive HTML snapshot downloads, and website screenshot image evidence.
- **Qdrant**: (Optional integration module) Vector DB for deep semantic storage of educational taxonomy constraints.

### 3. Distributed Processing Pipeline (Workers)
- **Celery + Redis**: The backbone of the verification engine. By using message broker queues, the platform processes millions of rows without locking the API or dropping tasks.
- **Ingestion Worker**: Securely downloads PDFs, utilizes `PyMuPDF` to intelligently chunk visual layout grid data, and dispatches thousands of rows onto the scraper queue.
- **Scraper Worker**: An infinitely scalable pool of `Playwright` browsers. Designed to handle network timeouts, spoof user agents, bypass WAFs, dump HTML contexts, take physical screenshots, and dispatch records to the AI layer.
- **Validation & AI Worker**: A dual-layered waterfall engine:
  - *Layer 1 (ML)*: Lightning fast semantic verification using `sentence-transformers` and `XGBoost`.
  - *Layer 2 (LLM)*: Deep reasoning fallback using massive offline local models (`Ollama` + `gemma4:31b-cloud` or `llama3.2`) to catch nuanced discrepancies if ML confidence drops.

---

## 🚀 Getting Started

To run the platform locally, ensure you have **Docker** and **Node.js** installed.

### Step 1: Boot up the Infrastructure
Spin up the massive backend infrastructure (PostgreSQL, Redis, MinIO, Qdrant) alongside the Celery Worker processes and the FastAPI backend.

```bash
docker-compose up --build
```

### Step 2: Boot up the Frontend Dashboard
Navigate to the Next.js frontend and start the interactive dashboard.

```bash
cd frontend
npm install
npm run dev
```

### Step 3: Local AI Configuration (Optional)
If you wish to use local open-source LLMs entirely offline, ensure Ollama is installed and running on your machine:
```bash
ollama pull gemma4:31b-cloud
```
The AI Verification worker will automatically connect to `http://localhost:11434/v1` to execute fallback reasoning.

---

## 📂 Project Structure

- **`/frontend`**: The Next.js 15 App Router web application.
- **`/backend`**: The primary Python directory.
  - **`/app/main.py`**: The FastAPI ASGI application entrypoint.
  - **`/app/api/`**: REST endpoints (`/jobs`).
  - **`/app/core/`**: Configuration, Database session management, S3 connections, and Celery app setup.
  - **`/app/models/`**: SQLAlchemy Database Schema blueprints.
  - **`/app/schemas/`**: Pydantic Data Validation definitions.
  - **`/app/workers/`**: The distributed Celery background tasks (`ingestion`, `scraper`, `ai_engine`).
- **`/infrastructure`**: Advanced deployment orchestration configuration files.
- **`/shared`**: Shared Python utilities mapping domain rules and taxonomy.
- **`docker-compose.yml`**: The universal control plane for booting all microservices simultaneously.
