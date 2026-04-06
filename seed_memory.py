import asyncio
import uuid
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import the configured agent from vanna_setup.py
from vanna_setup import agent, agent_memory  # noqa: E402, F401

# Correct Vanna 2.0 imports
from vanna.capabilities.agent_memory import ToolMemory  # noqa: E402
from vanna.core.tool import ToolContext  # noqa: E402
from vanna.core.user import User  # noqa: E402

# ─────────────────────────────────────────────────────────────
# DEFAULT USER
# Must match the group_memberships in vanna_setup.py
# ─────────────────────────────────────────────────────────────
DEFAULT_USER = User(
    id="default_user",
    email="intern@clinic.com",
    group_memberships=["users","admin"]
)

# ToolContext now requires user, conversation_id, request_id, agent_memory
TOOL_CONTEXT = ToolContext(
    user=DEFAULT_USER,
    conversation_id=str(uuid.uuid4()),
    request_id=str(uuid.uuid4()),
    agent_memory=agent_memory
)

# ─────────────────────────────────────────────────────────────
# 21 QUESTION-SQL PAIRS
# Covers all required categories:
#   - Patient queries
#   - Doctor queries
#   - Appointment queries
#   - Financial queries
#   - Time-based queries
# ─────────────────────────────────────────────────────────────
QA_PAIRS = [

    # ── PATIENT QUERIES ──────────────────────────────────────
    {
        "question": "How many patients do we have?",
        "sql":      "SELECT COUNT(*) AS total_patients FROM patients"
    },
    {
        "question": "List all patients",
        "sql": (
            "SELECT first_name, last_name, email, phone, city, gender "
            "FROM patients "
            "ORDER BY last_name, first_name"
        )
    },
    {
        "question": "How many male and female patients do we have?",
        "sql": (
            "SELECT gender, COUNT(*) AS count "
            "FROM patients "
            "GROUP BY gender"
        )
    },
    {
        "question": "Which city has the most patients?",
        "sql": (
            "SELECT city, COUNT(*) AS patient_count "
            "FROM patients "
            "GROUP BY city "
            "ORDER BY patient_count DESC "
            "LIMIT 1"
        )
    },
    {
        "question": "Show patient count by city",
        "sql": (
            "SELECT city, COUNT(*) AS patient_count "
            "FROM patients "
            "GROUP BY city "
            "ORDER BY patient_count DESC"
        )
    },
    {
        "question": "List patients who visited more than 3 times",
        "sql": (
            "SELECT p.first_name, p.last_name, COUNT(a.id) AS visit_count "
            "FROM patients p "
            "JOIN appointments a ON a.patient_id = p.id "
            "GROUP BY p.id, p.first_name, p.last_name "
            "HAVING COUNT(a.id) > 3 "
            "ORDER BY visit_count DESC"
        )
    },

    # ── DOCTOR QUERIES ───────────────────────────────────────
    {
        "question": "List all doctors and their specializations",
        "sql": (
            "SELECT name, specialization, department, phone "
            "FROM doctors "
            "ORDER BY specialization, name"
        )
    },
    {
        "question": "Which doctor has the most appointments?",
        "sql": (
            "SELECT d.name, d.specialization, COUNT(a.id) AS appointment_count "
            "FROM doctors d "
            "JOIN appointments a ON a.doctor_id = d.id "
            "GROUP BY d.id, d.name, d.specialization "
            "ORDER BY appointment_count DESC "
            "LIMIT 1"
        )
    },
    {
        "question": "Show number of appointments per doctor",
        "sql": (
            "SELECT d.name, d.specialization, COUNT(a.id) AS appointment_count "
            "FROM doctors d "
            "LEFT JOIN appointments a ON a.doctor_id = d.id "
            "GROUP BY d.id, d.name, d.specialization "
            "ORDER BY appointment_count DESC"
        )
    },

    # ── APPOINTMENT QUERIES ──────────────────────────────────
    {
        "question": "Show me appointments for last month",
        "sql": (
            "SELECT p.first_name, p.last_name, d.name AS doctor, "
            "a.appointment_date, a.status "
            "FROM appointments a "
            "JOIN patients p ON p.id = a.patient_id "
            "JOIN doctors  d ON d.id = a.doctor_id "
            "WHERE strftime('%Y-%m', a.appointment_date) "
            "    = strftime('%Y-%m', date('now', '-1 month')) "
            "ORDER BY a.appointment_date DESC"
        )
    },
    {
        "question": "How many cancelled appointments are there?",
        "sql": (
            "SELECT COUNT(*) AS cancelled_count "
            "FROM appointments "
            "WHERE status = 'Cancelled'"
        )
    },
    {
        "question": "How many cancelled appointments last quarter?",
        "sql": (
            "SELECT COUNT(*) AS cancelled_count "
            "FROM appointments "
            "WHERE status = 'Cancelled' "
            "  AND appointment_date >= date('now', '-3 months')"
        )
    },
    {
        "question": "Show monthly appointment count for the past 6 months",
        "sql": (
            "SELECT strftime('%Y-%m', appointment_date) AS month, "
            "COUNT(*) AS appointment_count "
            "FROM appointments "
            "WHERE appointment_date >= date('now', '-6 months') "
            "GROUP BY strftime('%Y-%m', appointment_date) "
            "ORDER BY month ASC"
        )
    },
    {
        "question": "What percentage of appointments are no-shows?",
        "sql": (
            "SELECT ROUND( "
            "    100.0 * SUM(CASE WHEN status = 'No-Show' THEN 1 ELSE 0 END) "
            "    / COUNT(*), 2 "
            ") AS no_show_percentage "
            "FROM appointments"
        )
    },

    # ── FINANCIAL QUERIES ────────────────────────────────────
    {
        "question": "What is the total revenue?",
        "sql": (
            "SELECT ROUND(SUM(total_amount), 2) AS total_revenue "
            "FROM invoices"
        )
    },
    {
        "question": "Show revenue by doctor",
        "sql": (
            "SELECT d.name AS doctor_name, d.specialization, "
            "ROUND(SUM(i.total_amount), 2) AS total_revenue "
            "FROM invoices i "
            "JOIN appointments a ON a.patient_id = i.patient_id "
            "JOIN doctors d      ON d.id = a.doctor_id "
            "GROUP BY d.id, d.name, d.specialization "
            "ORDER BY total_revenue DESC"
        )
    },
    {
        "question": "Show unpaid invoices",
        "sql": (
            "SELECT p.first_name, p.last_name, "
            "i.invoice_date, i.total_amount, i.paid_amount, "
            "ROUND(i.total_amount - i.paid_amount, 2) AS balance_due, "
            "i.status "
            "FROM invoices i "
            "JOIN patients p ON p.id = i.patient_id "
            "WHERE i.status IN ('Pending', 'Overdue') "
            "ORDER BY i.status, i.total_amount DESC"
        )
    },
    {
        "question": "Top 5 patients by total spending",
        "sql": (
            "SELECT p.first_name, p.last_name, "
            "ROUND(SUM(i.total_amount), 2) AS total_spending "
            "FROM invoices i "
            "JOIN patients p ON p.id = i.patient_id "
            "GROUP BY p.id, p.first_name, p.last_name "
            "ORDER BY total_spending DESC "
            "LIMIT 5"
        )
    },
    {
        "question": "Average treatment cost by specialization",
        "sql": (
            "SELECT d.specialization, "
            "ROUND(AVG(t.cost), 2) AS avg_cost, "
            "COUNT(t.id) AS treatment_count "
            "FROM treatments t "
            "JOIN appointments a ON a.id = t.appointment_id "
            "JOIN doctors d      ON d.id = a.doctor_id "
            "GROUP BY d.specialization "
            "ORDER BY avg_cost DESC"
        )
    },

    # ── TIME-BASED QUERIES ───────────────────────────────────
    {
        "question": "Show revenue trend by month",
        "sql": (
            "SELECT strftime('%Y-%m', invoice_date) AS month, "
            "ROUND(SUM(total_amount), 2) AS monthly_revenue "
            "FROM invoices "
            "GROUP BY strftime('%Y-%m', invoice_date) "
            "ORDER BY month ASC"
        )
    },
    {
        "question": "Show patient registration trend by month",
        "sql": (
            "SELECT strftime('%Y-%m', registered_date) AS month, "
            "COUNT(*) AS new_patients "
            "FROM patients "
            "GROUP BY strftime('%Y-%m', registered_date) "
            "ORDER BY month ASC"
        )
    },
]


# ─────────────────────────────────────────────────────────────
# SEED FUNCTION
# ─────────────────────────────────────────────────────────────
async def seed_memory():
    print("=" * 55)
    print("  Seeding Vanna 2.0 Agent Memory")
    print("=" * 55)
    print(f"  Total Q&A pairs to seed: {len(QA_PAIRS)}")
    print("-" * 55)

    success_count = 0
    fail_count    = 0

    for i, pair in enumerate(QA_PAIRS, start=1):
        question = pair["question"]
        sql      = pair["sql"].strip()

        try:
            # Build a ToolMemory object for each Q&A pair
            memory_item = ToolMemory(
                question=question,
                tool_name="run_sql",
                args={"sql": sql}
            )

            # Save it into agent memory using the correct Vanna 2.0 method
            await agent_memory.save_tool_usage(
                question=memory_item.question,
                tool_name=memory_item.tool_name,
                args=memory_item.args,
                context=TOOL_CONTEXT,
                success=True
            )

            print(f"  ✅ [{i:02d}/{len(QA_PAIRS)}] {question}")
            success_count += 1

        except Exception as e:
            print(f"  ❌ [{i:02d}/{len(QA_PAIRS)}] FAILED: {question}")
            print(f"          Error: {e}")
            fail_count += 1

    print("-" * 55)
    print(f"  ✅ Successfully seeded : {success_count}/{len(QA_PAIRS)}")
    if fail_count > 0:
        print(f"  ❌ Failed             : {fail_count}/{len(QA_PAIRS)}")
    print("=" * 55)
    print("  Agent memory is ready!")
    print("=" * 55)


# ─────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(seed_memory())