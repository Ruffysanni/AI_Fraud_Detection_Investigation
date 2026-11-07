# Fraud Detection and Investigation Platform

A full-stack prototype that combines machine learning, rule-based anomaly detection, retrieval-augmented generation (RAG), and structured evidence synthesis to support financial transaction fraud investigations.

## 1. Project Overview

The platform provides an end-to-end workflow for assessing financial transactions and supporting the investigation of potentially suspicious activity.

Users submit transaction information through a React dashboard. The FastAPI backend processes the transaction using a trained machine learning model, generates a fraud risk score, assigns a risk classification, and stores the assessment in PostgreSQL.

When a transaction meets the configured risk criteria, an investigation alert is created.

The platform also provides an investigation workflow that collects transaction details, machine learning assessments, rule-based observations, potentially comparable transactions, and relevant knowledge-base guidance. The collected information is validated, classified, and assessed before a structured investigation report is generated.

**Important:** A fraud prediction is a model estimate, not proof that fraud has occurred. All suspected activity requires appropriate human investigation and verification.

## 2. Key Features

- **Transaction assessment:** Accepts transaction information and returns a fraud prediction, probability score, and risk classification.
- **Machine learning:** Uses a trained scikit-learn model to estimate transaction fraud risk.
- **Rule-based anomaly detection:** Identifies potentially suspicious transaction patterns and balance movements.
- **Investigation alerts:** Creates and stores alerts for transactions assessed as medium or high risk.
- **Live dashboard:** Displays transaction activity, investigation alerts, and database-backed metrics.
- **RAG knowledge-base retrieval:** Retrieves relevant information from local Markdown documents using TF-IDF vectorization and cosine similarity.
- **Investigation tools:** Provides controlled Python functions for retrieving transaction details, risk scores, anomaly observations, guidance, comparable transactions, and saving findings.
- **Evidence synthesis:** Collects, validates, classifies, and assesses investigation evidence.
- **Structured reporting:** Generates investigation reports and exports them as JSON files.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React 19 |
| Frontend tooling | Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Database driver | Psycopg 3 |
| Machine learning | scikit-learn |
| Data processing | Pandas |
| Model persistence | Joblib |
| RAG retrieval | TF-IDF, cosine similarity |
| Report format | JSON |
| API documentation | FastAPI / Swagger UI |

## 4. System Architecture

The application follows a frontend–backend architecture.

1. **Frontend:** The React dashboard collects transaction information and displays assessments, metrics, transactions, and alerts.
2. **API layer:** FastAPI receives requests, validates inputs, coordinates the assessment workflow, and returns results.
3. **Machine learning layer:** The trained model produces a fraud probability and prediction.
4. **Database layer:** PostgreSQL stores assessed transactions, investigation alerts, and structured investigation findings.
5. **Investigation layer:** Controlled Python tools retrieve and analyze transaction information.
6. **RAG layer:** The document loader, text processor, vector store, and retriever provide relevant knowledge-base passages.
7. **Evidence synthesis layer:** Evidence is collected, validated, classified, and assessed.
8. **Reporting layer:** The report generator produces structured investigation reports and exports them to JSON.

## 5. Project Structure

```text
AI_Fraud_Detection_Investigation/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── investigation_tools.py
│   │   ├── evidence/
│   │   │   ├── evidence_assessor.py
│   │   │   ├── evidence_classifier.py
│   │   │   ├── evidence_collector.py
│   │   │   ├── evidence_schema.py
│   │   │   ├── evidence_synthesizer.py
│   │   │   └── evidence_validator.py
│   │   ├── rag/
│   │   │   ├── document_loader.py
│   │   │   ├── retrieval.py
│   │   │   ├── text_processor.py
│   │   │   └── vector_store.py
│   │   ├── reports/
│   │   │   └── report_generator.py
│   │   ├── database.py
│   │   ├── init_db.py
│   │   ├── main.py
│   │   └── train_model.py
│   │
│   ├── models/
│   │   ├── fraud_model.joblib
│   │   └── evaluation.json
│   └── requirements.txt
│
├── data/
│   ├── processed/
│   ├── raw/                 # Local raw dataset; not committed
│   └── reports/             # Generated reports; not committed
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── knowledge_base/
│   ├── fraud_indicators/
│   │   └── transaction_fraud_indicators.md
│   ├── investigation_procedures/
│   │   └── investigation_procedures.md
│   └── transaction_monitoring/
│       └── transaction_monitoring_procedures.md
│
├── .gitignore
└── README.md
```

## 6. Prerequisites

Install the following:

- Python 3.13
- Node.js and npm
- PostgreSQL
- Git

The repository should also contain the trained model artifact at:

`backend/models/fraud_model.joblib`

## 7. Installation and Setup

### 7.1 Clone the repository

```bash
git clone https://github.com/Ruffysanni/AI_Fraud_Detection_Investigation.git
```

Navigate into the project directory:

```bash
cd AI_Fraud_Detection_Investigation
```

### 7.2 Create a Python virtual environment

```bash
python -m venv .venv
```

Activate it in Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

### 7.3 Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 7.4 Create the PostgreSQL database

Open PostgreSQL using your preferred PostgreSQL client and execute:

```sql
CREATE DATABASE fraud_investigation_db;
```

### 7.5 Configure backend environment variables

Create a `.env` file in the project root.

Add the following configuration, replacing the example credentials with your own:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fraud_investigation_db
DB_USER=postgres
DB_PASSWORD=your_database_password
```

Keep this file private. Do not commit your `.env` file or expose database credentials.

### 7.6 Initialize the database tables

From the project root, run:

```bash
python -m backend.app.init_db
```

The initialization script creates these tables if they do not already exist:

- `transactions`
- `investigation_alerts`
- `investigation_findings`

### 7.7 Configure the frontend

Open another Git Bash terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create your local environment file:

```bash
cp .env.example .env
```

The default local configuration is:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 7.8 Start the backend

From the project root, with the virtual environment activated:

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 7.9 Start the frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

Open the local URL displayed by Vite, normally:

`http://localhost:5173`

Both the backend and frontend must be running for the dashboard to retrieve live information.

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks backend health |
| GET | `/dashboard/metrics` | Retrieves dashboard metrics |
| POST | `/predict` | Assesses a transaction |
| GET | `/transactions` | Retrieves assessed transactions |
| GET | `/alerts` | Retrieves investigation alerts |
| POST | `/reports/{transaction_id}/generate` | Generates and exports an investigation report |

The transaction endpoint supports a configurable result limit. The alerts endpoint supports filtering by alert status and a configurable result limit.

For request parameters, schemas, and response examples, visit `/docs`.

## 9. Investigation Workflow

The investigation workflow uses six controlled Python tools:

1. `get_transaction_details` — retrieves transaction information.
2. `get_fraud_risk_score` — retrieves the machine learning assessment and associated alert information.
3. `analyze_transaction_anomalies` — identifies rule-based transaction observations.
4. `search_fraud_policies` — retrieves relevant knowledge-base passages.
5. `get_related_transactions` — identifies potentially comparable transactions.
6. `save_investigation_findings` — saves structured findings to PostgreSQL.

The evidence synthesis process then:

- Collects information from the investigation tools.
- Validates the structure of the evidence package.
- Classifies evidence into relevant categories.
- Assesses evidence availability and limitations.
- Produces an overall investigation assessment.

The report generator uses the synthesized evidence to create a structured report containing transaction details, machine learning assessment, rule observations, comparable transactions, retrieved guidance, limitations, recommendations, and a disclaimer.

## 10. RAG Knowledge Base

The local knowledge base contains Markdown documents covering:

- Transaction fraud indicators.
- Investigation procedures.
- Transaction monitoring procedures.

The documents are loaded and split into overlapping text chunks. The text is then indexed using TF-IDF vectorization.

Retrieval uses cosine similarity to identify passages relevant to an investigation query. Retrieved passages include source information and similarity scores.

**Technical distinction:** The current implementation uses lexical TF-IDF retrieval. It does not currently use neural embedding models or a hosted vector database.

## 11. Investigation Report Generation

Reports can be generated using:

```text
POST /reports/{transaction_id}/generate
```

For example:

```bash
curl -X POST http://127.0.0.1:8000/reports/6/generate
```

Replace `6` with an existing transaction ID.

Generated reports are exported to:

`data/reports/`

The API returns the report ID, transaction ID, synthesis status, exported file path, and report content.

A report with a `partial` synthesis status can still be generated successfully. This indicates that some evidence or validation conditions were not fully satisfied. It should not be interpreted as a fully completed investigation.

## 12. Testing and Verification

The application has been exercised through backend and frontend workflows, including:

- Database connectivity and table initialization.
- Transaction assessment through the API and dashboard.
- Persistence of transaction assessments.
- Creation and retrieval of investigation alerts.
- Live dashboard metric updates.
- Evidence collection and validation.
- Handling of missing transactions and unavailable evidence sources.
- Investigation report generation.
- JSON report export and validity checks.
- Frontend production build.
- Backend Python compilation checks.

Frontend build:

```bash
cd frontend
npm run build
```

Frontend lint:

```bash
npm run lint
```

## 13. Current Limitations

This is a prototype intended to demonstrate an end-to-end fraud assessment and investigation workflow. It is not a production banking fraud platform.

- **Predictions are not proof:** Machine learning scores indicate estimated risk and require human review.
- **Correlated observations:** Some balance-movement rules describe related aspects of the same transaction and should not be treated as independent confirmations.
- **Comparable transactions:** The database does not currently store origin and destination account identifiers. Comparable records are selected using transaction type and amount, not verified account relationships.
- **Knowledge-base guidance:** The Markdown documents are illustrative prototype material, not official banking policies or regulatory requirements.
- **Retrieval approach:** TF-IDF and cosine similarity provide lexical retrieval rather than neural semantic retrieval.
- **Report generation:** Reports are generated using deterministic Python logic, not an LLM.
- **Agent orchestration:** Investigation tools are controlled Python functions. The current implementation does not use autonomous LLM agent orchestration.
- **Security:** The prototype does not yet implement production authentication, authorization, or a complete operational security model.

## 14. Future Improvements

Potential improvements include:

- Integrating Azure OpenAI for LLM-based investigation assistance and report generation.
- Integrating Azure AI Search for hosted vector and hybrid retrieval.
- Adding neural embeddings and document ingestion pipelines.
- Introducing LLM tool-calling with controlled permissions and validated tool outputs.
- Adding account identifiers and transaction relationship analysis.
- Implementing authentication, authorization, audit logging, and stronger production security.
- Deploying the frontend, backend, and database using suitable Azure services.

These are planned improvements, not features currently implemented.

## 15. Disclaimer

This platform is a demonstration and decision-support prototype. Its predictions, observations, retrieved guidance, and generated reports must not be treated as definitive findings of fraud. All suspected activity requires appropriate human investigation and verification.