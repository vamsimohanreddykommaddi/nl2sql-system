import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────────────────────
# VANNA 2.0 IMPORTS 
# ─────────────────────────────────────────────────────────────
from vanna import Agent, AgentConfig  # noqa: E402
from vanna.core.registry import ToolRegistry  # noqa: E402
from vanna.core.user import UserResolver, User, RequestContext  # noqa: E402

from vanna.tools import RunSqlTool, VisualizeDataTool  # noqa: E402
from vanna.tools.agent_memory import (  # noqa: E402
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
)

from vanna.integrations.sqlite import SqliteRunner  # noqa: E402
from vanna.integrations.local.agent_memory import DemoAgentMemory  # noqa: E402

# Gemini LLM (Vanna 2.0 integration)
from vanna.integrations.google import GeminiLlmService  # noqa: E402


# ─────────────────────────────────────────────────────────────
# STEP 1 — LLM SERVICE (Google Gemini)
# ─────────────────────────────────────────────────────────────
# gemini-2.5 flash is confirmed to work with Vanna 2.0
# Do NOT use gemini-3-x models — they have a known Vanna 2.0 bug
llm = GeminiLlmService(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash",
)


# ─────────────────────────────────────────────────────────────
# STEP 2 — DATABASE RUNNER (SQLite)
# ─────────────────────────────────────────────────────────────
# SqliteRunner handles all database connections for us
# We do NOT write a custom SQL runner — Vanna provides this
sql_runner = SqliteRunner(database_path="./clinic.db")


# ─────────────────────────────────────────────────────────────
# STEP 3 — AGENT MEMORY (DemoAgentMemory)
# ─────────────────────────────────────────────────────────────
# DemoAgentMemory is Vanna 2.0's learning system
# It stores successful question-SQL pairs so the agent improves over time
# This replaces the old vn.train() + ChromaDB approach from Vanna 0.x
agent_memory = DemoAgentMemory(max_items=1000)


# ─────────────────────────────────────────────────────────────
# STEP 4 — TOOL REGISTRY
# Register all the tools the agent is allowed to use
# ─────────────────────────────────────────────────────────────
tools = ToolRegistry()

# RunSqlTool  — lets the agent run SQL queries on our database
tools.register_local_tool(
    RunSqlTool(sql_runner=sql_runner),
    access_groups=["users"]
)

# VisualizeDataTool — lets the agent generate Plotly charts
tools.register_local_tool(
    VisualizeDataTool(),
    access_groups=["users"]
)

# SaveQuestionToolArgsTool — saves successful Q&A pairs into memory
tools.register_local_tool(
    SaveQuestionToolArgsTool(),
    access_groups=["users","admin"]
)

# SearchSavedCorrectToolUsesTool — searches memory for similar past questions
tools.register_local_tool(
    SearchSavedCorrectToolUsesTool(),
    access_groups=["users","admin"]
)


# ─────────────────────────────────────────────────────────────
# STEP 5 — USER RESOLVER
# A simple resolver that treats every request as the same default user
# In production this would check JWT tokens / cookies
# For this assignment, we keep it simple
# ─────────────────────────────────────────────────────────────
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(
            id="default_user",
            email="intern@clinic.com",
            group_memberships=["users", "admin"]
        )


# ─────────────────────────────────────────────────────────────
# STEP 6 — CREATE THE AGENT
# Wire everything together into one Agent instance
# ─────────────────────────────────────────────────────────────
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=SimpleUserResolver(),
    agent_memory=agent_memory,
    config=AgentConfig()
)


# ─────────────────────────────────────────────────────────────
# Run this file directly to verify the agent initializes correctly
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Vanna 2.0 Agent Setup Check")
    print("=" * 50)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("  ❌ ERROR: GOOGLE_API_KEY not found in .env file!")
        print("     Make sure your .env file contains: GOOGLE_API_KEY=your-key")
    else:
        print(f"  ✅ GOOGLE_API_KEY loaded ({api_key[:8]}...)")

    print("  ✅ LLM Service     : GeminiLlmService (gemini-2.5-flash)")
    print("  ✅ Database        : clinic.db (SQLite)")
    print("  ✅ Agent Memory    : DemoAgentMemory (max 1000 items)")
    print("  ✅ Tools Registered: RunSql, VisualizeData, SaveMemory, SearchMemory")
    print("  ✅ User Resolver   : SimpleUserResolver (default user)")
    print("  ✅ Agent           : Ready!")
    print("=" * 50)
    print("  Import this agent in other files using:")
    print("  from vanna_setup import agent")
    print("=" * 50)
