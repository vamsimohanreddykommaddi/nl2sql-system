import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# ─────────────────────────────────────────────────────────────
# FASTAPI IMPORTS
# ─────────────────────────────────────────────────────────────
from fastapi import FastAPI
from pydantic import BaseModel

# ─────────────────────────────────────────────────────────────
# VANNA 2.0 IMPORTS
# ─────────────────────────────────────────────────────────────
from vanna.servers.fastapi import VannaFastAPIServer

# ─────────────────────────────────────────────────────────────
# IMPORT OUR CONFIGURED AGENT
# ─────────────────────────────────────────────────────────────
from vanna_setup import agent, agent_memory

# ─────────────────────────────────────────────────────────────
# SQL VALIDATION
# Runs before any AI-generated SQL is executed
# Rejects anything that is not a safe SELECT query
# ─────────────────────────────────────────────────────────────
BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "EXEC", "EXECUTE", "xp_", "sp_", "GRANT", "REVOKE",
    "SHUTDOWN", "ATTACH", "DETACH", "TRUNCATE"
]

def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validates that the SQL is a safe SELECT query.
    Returns (is_valid, error_message).
    """
    if not sql or not sql.strip():
        return False, "SQL query is empty."

    sql_upper = sql.upper().strip()

    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed. This query was rejected for safety."

    # Check for blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword.upper() in sql_upper:
            return False, f"Query contains a forbidden keyword: '{keyword}'. Rejected for safety."

    return True, "OK"


# ─────────────────────────────────────────────────────────────
# CREATE FASTAPI APP USING VannaFastAPIServer
# This gives us the built-in /chat streaming UI out of the box
# We then add our own /health and /chat endpoints on top
# ─────────────────────────────────────────────────────────────
vanna_server = VannaFastAPIServer(
    agent=agent,
    config={
        "cors": {
            "enabled": True,
            "allow_origins": ["*"]
        }
    }
)

# Create the ASGI app from the Vanna server
app = vanna_server.create_app()


# ─────────────────────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    message:    str
    sql_query:  str | None = None
    columns:    list       = []
    rows:       list       = []
    row_count:  int        = 0
    chart:      dict | None = None
    chart_type: str | None = None
    error:      str | None = None


# ─────────────────────────────────────────────────────────────
# POST /chat  — Main endpoint
# Accepts a natural language question, generates SQL,
# validates it, executes it, and returns results
# ─────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    question = request.question.strip()

    # ── Input validation ─────────────────────────────────────
    if not question:
        return ChatResponse(
            message="Please provide a question.",
            error="Question cannot be empty."
        )

    if len(question) > 500:
        return ChatResponse(
            message="Your question is too long. Please keep it under 500 characters.",
            error="Question too long."
        )

    # ── Send question to Vanna agent ─────────────────────────
    try:
        # Collect all streamed components from the agent
        sql_query   = None
        rows        = []
        columns     = []
        message     = ""
        chart       = None
        chart_type  = None

        # agent.send_message streams UiComponents — we collect them all
        # For a simple REST endpoint we gather everything then respond
        from vanna.core.user import User, RequestContext

        user = User(
            id="default_user",
            email="intern@clinic.com",
            group_memberships=["users"]
        )

        # Build a simple request context
        request_context = RequestContext(
            headers={},
            cookies={},
            user=user
        )

        components = []
        async for component in agent.send_message(
            request_context=request_context,
            message=question
        ):
            components.append(component)

        # ── Parse components ──────────────────────────────────
        for component in components:
            comp_type = type(component).__name__.lower()

            # Extract SQL from code block components
            if "code" in comp_type or "sql" in comp_type:
                try:
                    sql_query = component.code if hasattr(component, "code") else str(component)
                except Exception:
                    pass

            # Extract table data from dataframe components
            if "dataframe" in comp_type or "table" in comp_type:
                try:
                    if hasattr(component, "records") and component.records:
                        rows    = [list(r.values()) for r in component.records]
                        columns = list(component.records[0].keys()) if component.records else []
                except Exception:
                    pass

            # Extract text message
            if "text" in comp_type or "message" in comp_type:
                try:
                    msg = component.text if hasattr(component, "text") else str(component)
                    if msg and len(msg) > len(message):
                        message = msg
                except Exception:
                    pass

            # Extract chart
            if "chart" in comp_type or "plotly" in comp_type:
                try:
                    chart      = component.figure if hasattr(component, "figure") else None
                    chart_type = "bar"
                except Exception:
                    pass

        # ── SQL Validation ────────────────────────────────────
        if sql_query:
            is_valid, validation_msg = validate_sql(sql_query)
            if not is_valid:
                return ChatResponse(
                    message=f"The AI generated an unsafe query. {validation_msg}",
                    error=validation_msg
                )

        # ── No results ────────────────────────────────────────
        if not rows and not message:
            message = "No data found for your question. Try rephrasing it."

        if not message:
            message = f"Found {len(rows)} result(s) for your question."

        return ChatResponse(
            message=message,
            sql_query=sql_query,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            chart=chart,
            chart_type=chart_type
        )

    # ── Error handling ────────────────────────────────────────
    except ValueError as e:
        return ChatResponse(
            message="The AI could not generate valid SQL for your question. Please rephrase.",
            error=str(e)
        )

    except sqlite3.Error as e:
        return ChatResponse(
            message="The database query failed. Please try again.",
            error=f"Database error: {str(e)}"
        )

    except Exception as e:
        return ChatResponse(
            message="Something went wrong. Please try again.",
            error=str(e)
        )


# ─────────────────────────────────────────────────────────────
# GET /health  — Health check endpoint
# Returns status of the API, database, and agent memory
# ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():

    # Check database connection
    db_status = "disconnected"
    try:
        conn = sqlite3.connect("clinic.db")
        conn.execute("SELECT COUNT(*) FROM patients")
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # Check agent memory item count
    memory_count = 0
    try:
        memory_count = len(agent_memory.memories) if hasattr(agent_memory, "memories") else 0
    except Exception:
        memory_count = 0

    return {
        "status":              "ok",
        "database":            db_status,
        "agent_memory_items":  memory_count,
        "llm":                 "gemini-2.5-flash",
        "version":             "1.0.0"
    }


# ─────────────────────────────────────────────────────────────
# RUN DIRECTLY
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
