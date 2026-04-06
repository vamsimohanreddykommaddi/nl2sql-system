# NL2SQL Clinic System

An AI-powered **Natural Language to SQL (NL2SQL)** chatbot built with **Vanna AI 2.0** and **FastAPI**.
Users can ask questions in plain English and get results from a clinic database without writing any SQL.

> Built as part of the AI/ML Developer Intern Technical Screening Assignment.

---

## Project Description

This system allows users to interact with a **SQLite clinic database** using natural language.
Instead of writing SQL queries manually, users simply type a question like
*"Which doctor has the most appointments?"* and the system automatically:

1. Receives the natural language question
2. Uses **Google Gemini AI** (via Vanna AI 2.0) to generate the appropriate SQL query
3. Validates the SQL for safety — only SELECT queries are allowed
4. Executes the SQL against the clinic database
5. Returns the results along with a natural language summary

The clinic database contains 5 tables — patients, doctors, appointments, treatments,
and invoices — with realistic dummy data covering 200 patients, 15 doctors, 500 appointments,
350 treatments, and 300 invoices.

**Example interaction:**

- User asks: *"What is the total revenue?"*
- System generates: `SELECT ROUND(SUM(total_amount), 2) AS total_revenue FROM invoices`
- System returns: the total revenue figure with a natural language summary

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Backend language |
| Vanna AI | 2.0.x | NL2SQL Agent framework |
| FastAPI | Latest | REST API framework |
| SQLite | Built-in | Database (no installation needed) |
| Google Gemini | gemini-2.5-flash | LLM for SQL generation |
| Plotly | Latest | Chart generation |
| python-dotenv | Latest | Environment variable management |

---

## Project Structure

```
nl2sql-system/
├── setup_database.py   # Creates SQLite schema and inserts all dummy data
├── vanna_setup.py      # Vanna 2.0 Agent initialization and configuration
├── seed_memory.py      # Seeds agent memory with 21 example Q&A pairs
├── main.py             # FastAPI application with /chat and /health endpoints
├── requirements.txt    # All Python dependencies
├── README.md           # This file
├── RESULTS.md          # Test results for all 20 questions
├── clinic.db           # Generated SQLite database file
└── .env                # API keys — never committed to Git
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher installed
- A Google Gemini API key (free — instructions below)
- Git installed

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/vamsimohanreddykommaddi/nl2sql-system.git
cd nl2sql-system
```

---

### Step 2 — Create a Virtual Environment

**Windows:**
```powershell
python -m venv nl2sqlenv
nl2sqlenv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv nl2sqlenv
source nl2sqlenv/bin/activate
```

Once activated, your terminal prompt will show `(nl2sqlenv)` at the start.

---

### Step 3 — Install All Dependencies

```bash
pip install -r requirements.txt
```

This installs Vanna AI 2.0, FastAPI, Uvicorn, Plotly, Pandas, and all other required packages.

---

### Step 4 — Get a Free Google Gemini API Key

1. Go to **https://aistudio.google.com/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"** → **"Create API key in new project"**
4. Copy the generated key (starts with `AIzaSy...`)

---

### Step 5 — Set Up Environment Variables

Create a `.env` file in the project root folder:

```
GOOGLE_API_KEY=your-gemini-api-key-here
```

> Never commit the `.env` file to Git. It is already listed in `.gitignore`.

---

### Step 6 — Create the Database

Run the database setup script to create the schema and insert all dummy data:

```bash
python setup_database.py
```

Expected output:
```
==================================================
  Clinic Database Setup
==================================================
Creating tables...
  ✓ All tables created.
Inserting doctors...
  ✓ Inserted 15 doctors.
Inserting patients...
  ✓ Inserted 200 patients.
Inserting appointments...
  ✓ Inserted 500 appointments.
Inserting treatments...
  ✓ Inserted 350 treatments.
Inserting invoices...
  ✓ Inserted 300 invoices.

==================================================
  ✅ Database setup complete!
  📁 File created : clinic.db
  👨‍⚕️ Doctors       : 15
  🧑 Patients      : 200
  📅 Appointments  : 500
  💊 Treatments    : 350
  🧾 Invoices      : 300
==================================================
```

This creates the file `clinic.db` in your project folder.

---

## How to Run the Memory Seeding Script

The memory seeding script pre-loads the agent with 21 known good question-SQL pairs
so it has a head start before any user asks questions.

```bash
python seed_memory.py
```

Expected output:
```
=======================================================
  Seeding Vanna 2.0 Agent Memory
=======================================================
  Total Q&A pairs to seed: 21
-------------------------------------------------------
  ✅ [01/21] How many patients do we have?
  ✅ [02/21] List all patients
  ✅ [03/21] How many male and female patients do we have?
  ...
  ✅ [21/21] Show patient registration trend by month
-------------------------------------------------------
  ✅ Successfully seeded : 21/21
=======================================================
  Agent memory is ready!
=======================================================
```

The seeded pairs cover patient queries, doctor queries, appointment queries,
financial queries, and time-based queries.

> Run this script every time you restart the project, since DemoAgentMemory
> is in-memory and does not persist between server restarts.

---

## How to Start the API Server

```bash
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['D:\\nl2sql-system']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

The server is now running. You can access:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Built-in Vanna chat UI |
| `http://localhost:8000/chat` | POST endpoint for questions |
| `http://localhost:8000/health` | GET health check |
| `http://localhost:8000/docs` | Swagger API documentation |

To stop the server, press `Ctrl+C` in the terminal.

---

## API Documentation

### POST /chat

Accepts a natural language question and returns SQL results with a summary.

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many patients do we have?"}'
```

**Request Body:**
```json
{
  "question": "How many patients do we have?"
}
```

**Success Response:**
```json
{
  "message": "We have 200 patients.",
  "sql_query": "SELECT COUNT(*) FROM patients",
  "columns": ["count(*)"],
  "rows": [[200]],
  "row_count": 1,
  "chart": null,
  "chart_type": null,
  "error": null
}
```

**Another Example — Revenue by Doctor:**

Request:
```json
{
  "question": "Show revenue by doctor"
}
```

Response:
```json
{
  "message": "Here is the revenue breakdown by doctor.",
  "sql_query": "SELECT d.name, ROUND(SUM(i.total_amount), 2) AS total_revenue FROM invoices i JOIN appointments a ON a.patient_id = i.patient_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.id, d.name ORDER BY total_revenue DESC",
  "columns": ["name", "total_revenue"],
  "rows": [
    ["Dr. Suresh Reddy", 45230.50],
    ["Dr. Priya Sharma", 38120.00]
  ],
  "row_count": 15,
  "chart": null,
  "chart_type": null,
  "error": null
}
```

**Validation Error Response** (when unsafe SQL is generated):
```json
{
  "message": "Only SELECT queries are allowed. This query was rejected for safety.",
  "sql_query": null,
  "columns": [],
  "rows": [],
  "row_count": 0,
  "chart": null,
  "chart_type": null,
  "error": "SQL validation failed"
}
```

**Input Validation Error** (empty question):
```json
{
  "message": "Please provide a question.",
  "sql_query": null,
  "columns": [],
  "rows": [],
  "row_count": 0,
  "chart": null,
  "chart_type": null,
  "error": "Question cannot be empty."
}
```

---

### GET /health

Returns the current health status of the API, database, and agent memory.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "agent_memory_items": 21,
  "llm": "gemini-2.5-flash",
  "version": "1.0.0"
}
```

---

## Architecture Overview

The system follows a simple pipeline from question to result:

```
┌─────────────────────────────────────────────────┐
│                   User                          │
│     "Which doctor has the most appointments?"   │
└────────────────────┬────────────────────────────┘
                     │ HTTP POST /chat
                     ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                    │
│                  main.py                        │
│                                                 │
│  1. Input Validation                            │
│     - Check question is not empty               │
│     - Check length under 500 characters         │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│            Vanna 2.0 Agent                      │
│              vanna_setup.py                     │
│                                                 │
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │ GeminiLlmService│  │   DemoAgentMemory    │  │
│  │ gemini-2.5-flash│  │  (21 seeded Q&A      │  │
│  │                 │  │   pairs for context) │  │
│  └────────┬────────┘  └──────────────────────┘  │
│           │                                     │
│           ▼                                     │
│     Generates SQL query                         │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              SQL Validation                     │
│                                                 │
│  - Must start with SELECT                       │
│  - No INSERT / UPDATE / DELETE / DROP           │
│  - No EXEC / GRANT / SHUTDOWN                   │
│  - No ATTACH / DETACH / TRUNCATE                │
│                                                 │
│  If invalid → return error, do NOT execute      │
└────────────────────┬────────────────────────────┘
                     │ Valid SQL only
                     ▼
┌─────────────────────────────────────────────────┐
│           SQLite Database                       │
│              clinic.db                          │
│                                                 │
│  Tables: patients, doctors, appointments,       │
│          treatments, invoices                   │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              Response                           │
│                                                 │
│  - Natural language summary                     │
│  - Generated SQL query                          │
│  - Result columns and rows                      │
│  - Row count                                    │
│  - Optional Plotly chart                        │
└─────────────────────────────────────────────────┘
```

### Key Components

**`setup_database.py`** — Creates the SQLite clinic database with 5 tables and
populates it with realistic dummy data including 200 patients, 15 doctors across
5 specializations, 500 appointments, 350 treatments, and 300 invoices.

**`vanna_setup.py`** — Initializes the Vanna 2.0 Agent by wiring together the
GeminiLlmService (AI brain), SqliteRunner (database connection), DemoAgentMemory
(learning system), ToolRegistry (available tools), and SimpleUserResolver (auth).

**`seed_memory.py`** — Pre-loads the agent with 21 known correct question-SQL
pairs so it performs better from the first query.

**`main.py`** — FastAPI application that exposes the `/chat` and `/health`
endpoints. Includes SQL validation to ensure only safe SELECT queries are executed,
and error handling for invalid SQL, database failures, and empty results.

---

## LLM Provider

This project uses **Google Gemini** (`gemini-2.5-flash`) via Vanna AI 2.0's
`GeminiLlmService` integration.

**Why Gemini was chosen:**
- Free tier available with no credit card required
- Strong performance on structured SQL generation tasks
- Native integration with Vanna AI 2.0
- Simple setup requiring only a single API key

**Free tier limits:**
- 1500 requests per day for gemini-2.0-flash
- Rate limit: 15 requests per minute

> If you hit rate limits during testing, wait 60 seconds between questions
> or create a new API key from a different Google account.

---

## Known Issues

| Issue | Description | Workaround |
|-------|-------------|------------|
| Column hallucination | Agent occasionally guesses wrong column names for complex queries | Rephrase question with more specific table hints |
| Rate limiting | Gemini free tier limits requests per minute | Wait 30-60 seconds between questions during bulk testing |
| Memory not persistent | DemoAgentMemory resets on server restart | Run `seed_memory.py` again after each restart |
| Multi-table JOINs | 3-table JOIN queries through appointments occasionally fail | These are documented in RESULTS.md with correct SQL |
