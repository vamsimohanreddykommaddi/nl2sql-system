# Test Results — NL2SQL Clinic System

## Summary

| Metric | Value |
|--------|-------|
| Total Questions Tested | 20 |
| Passed (Correct SQL + Result) | 10 / 20 |
| Failed (Wrong SQL or Error) | 8 / 20 |
| Partial (SQL ran but result incorrect) | 2 / 20 |
| LLM Used | Google Gemini (gemini-2.5-flash) |
| Database | clinic.db (SQLite) |
| Test Date | 06-04-2026 |

---

## How to Read This Document

- ✅ **Passed** — Agent generated correct SQL and returned expected results
- ❌ **Failed** — Agent generated wrong SQL or returned a database error
- ⚠️ **Partial** — Agent returned results but SQL was not fully correct

---

## Detailed Results

---

### Q1 — How many patients do we have?

**Expected Behavior:** Returns a total count of all patients

**Generated SQL:**
```sql
SELECT COUNT(*) FROM patients
```

**Result:**
```
count(*) = 200
```

**Agent Response:** "We have 200 patients."

**Status:** ✅ Passed

**Notes:** Returned the correct count of 200 patients exactly as expected.

---

### Q2 — List all doctors and their specializations

**Expected Behavior:** Returns doctor list with their specializations

**Generated SQL:**
```sql
SELECT name, specialization FROM doctors
```

**Result:**
```
name                  | specialization
----------------------|---------------
Dr. Suresh Reddy      | Dermatology
Dr. Priya Sharma      | Dermatology
...
(15 rows, 2 columns)
```

**Status:** ✅ Passed

**Notes:** Returned all 15 doctors with their specializations correctly.

---

### Q3 — Show me appointments for last month

**Expected Behavior:** Filters appointments by date for last month

**Generated SQL:**
```sql
SELECT * FROM appointments
WHERE strftime('%Y-%m', appointment_date)
    = strftime('%Y-%m', date('now', '-1 month'))
```

**Result:**
```
id | patient_id | doctor_id | appointment_date      | status    | notes
---|------------|-----------|----------------------|-----------|----------------------
2  | 19         | 10        | 2026-03-08 00:22:07  | Scheduled | Follow-up required
10 | 38         | 10        | 2026-03-02 03:52:07  | Completed | null
11 | 6          | 3         | 2026-03-12 04:22:07  | Cancelled | null
...
(Multiple rows for March 2026)
```

**Status:** ✅ Passed

**Notes:** Correctly filtered appointments for March 2026 (last month relative to April 2026).

---

### Q4 — Which doctor has the most appointments?

**Expected Behavior:** Returns one doctor with highest appointment count

**Generated SQL:**
```sql
SELECT d.name, COUNT(a.id) AS num_appointments
FROM Doctors d
JOIN Appointments a ON d.id = a.doctor_id
GROUP BY d.name
ORDER BY num_appointments DESC
LIMIT 1
```

**Result:**
```
name              | num_appointments
------------------|------------------
(Doctor name)     | (count)
```

**Status:** ✅ Passed

**Notes:** Correctly used GROUP BY with COUNT and ORDER BY to find the busiest doctor.

---

### Q5 — What is the total revenue?

**Expected Behavior:** Returns SUM of all invoice total_amount values

**Generated SQL:**
```sql
SELECT SUM(price) AS total_revenue FROM Appointments
```

**Result:**
```
Error executing query: no such column: price
```

**Status:** ❌ Failed

**Notes:** The agent hallucinated a `price` column on the `Appointments` table. Revenue data
is stored in the `invoices` table under the column `total_amount`. The correct SQL is:
```sql
SELECT ROUND(SUM(total_amount), 2) AS total_revenue FROM invoices
```

---

### Q6 — Show revenue by doctor

**Expected Behavior:** JOIN invoices + appointments + doctors, GROUP BY doctor

**Generated SQL:**
```sql
SELECT d.name AS doctor_name, SUM(a.price) AS total_revenue
FROM doctors d
JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.name
ORDER BY total_revenue DESC
```

**Result:**
```
Error executing query: no such column: a.price
```

**Status:** ❌ Failed

**Notes:** Two errors — the agent used `a.price` (does not exist) instead of `i.total_amount`
from the invoices table, and also tried to JOIN using `d.doctor_id` which does not exist
(correct column is `d.id`). This requires a 3-table JOIN through appointments to invoices.
Correct SQL:
```sql
SELECT d.name, ROUND(SUM(i.total_amount), 2) AS total_revenue
FROM invoices i
JOIN appointments a ON a.patient_id = i.patient_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.id, d.name
ORDER BY total_revenue DESC
```

---

### Q7 — How many cancelled appointments last quarter?

**Expected Behavior:** COUNT with status filter and date range

**Generated SQL:**
```sql
SELECT COUNT(*) FROM appointments
WHERE status = 'Cancelled'
AND appointment_date >= DATE('now', '-3 months')
```

**Result:**
```
There were 27 cancelled appointments in the last quarter.
```

**Status:** ✅ Passed

**Notes:** Correctly filtered by both status and date range. Returned 27 cancelled appointments.

---

### Q8 — Top 5 patients by spending

**Expected Behavior:** JOIN patients + invoices, SUM total_amount, ORDER, LIMIT 5

**Generated SQL:**
```sql
SELECT p.name AS patient_name, SUM(a.cost) AS total_spending
FROM patients p
JOIN appointments a ON p.patient_id = a.patient_id
GROUP BY p.name
ORDER BY total_spending DESC
LIMIT 5
```

**Result:**
```
Error executing query: no such column: p.name
```

**Status:** ❌ Failed

**Notes:** The agent used `p.name` (does not exist) — the patients table has `first_name`
and `last_name` as separate columns. It also used `a.cost` from appointments instead of
`i.total_amount` from invoices. Correct SQL:
```sql
SELECT p.first_name, p.last_name,
       ROUND(SUM(i.total_amount), 2) AS total_spending
FROM invoices i
JOIN patients p ON p.id = i.patient_id
GROUP BY p.id, p.first_name, p.last_name
ORDER BY total_spending DESC
LIMIT 5
```

---

### Q9 — List patients who visited more than 3 times

**Expected Behavior:** Uses HAVING clause with COUNT of appointments

**Generated SQL:**
```sql
SELECT patient_id, COUNT(*) AS visit_count
FROM appointments
GROUP BY patient_id
HAVING COUNT(*) > 3
ORDER BY visit_count DESC
```

**Result:**
```
(Multiple patient_ids with visit counts > 3)
```

**Status:** ⚠️ Partial

**Notes:** SQL logic is correct and HAVING clause works properly. However, result shows
only `patient_id` numbers instead of patient names — a more complete query would JOIN
with the patients table to show `first_name` and `last_name`. Functionally correct but
not fully user-friendly.

---

### Q10 — Which city has the most patients?

**Expected Behavior:** GROUP BY city + COUNT + ORDER + LIMIT 1

**Generated SQL:**
```sql
SELECT city, COUNT(*) AS patient_count
FROM patients
GROUP BY city
ORDER BY patient_count DESC
LIMIT 1
```

**Result:**
```
city      | patient_count
----------|---------------
(city)    | (count)
(1 row, 2 columns)
```

**Status:** ✅ Passed

**Notes:** Perfectly correct SQL. Returned the city with the highest patient count.

---

### Q11 — Show monthly appointment count for the past 6 months

**Expected Behavior:** Groups appointments by month using date functions

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', appointment_date) AS month,
       COUNT(*) AS appointment_count
FROM appointments
WHERE appointment_date >= DATE('now', '-6 months')
GROUP BY month
ORDER BY month
```

**Result:**
```
month   | appointment_count
--------|------------------
(7 rows, 2 columns)
```

**Status:** ✅ Passed

**Notes:** Correctly used `strftime` for date grouping and filtered to past 6 months.
Returned 7 rows (6 complete months + current partial month).

---

### Q12 — Average treatment cost by specialization

**Expected Behavior:** 3-table JOIN — treatments + appointments + doctors, AVG(cost)

**Generated SQL:**
```sql
SELECT d.specialization, AVG(a.price) AS average_treatment_cost
FROM doctors d
JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.specialization
ORDER BY average_treatment_cost DESC
```

**Result:**
```
Error executing query: no such column: a.price
```

**Status:** ❌ Failed

**Notes:** Same hallucination pattern — agent used `a.price` on appointments table which
does not exist. Treatment cost is in `treatments.cost` and requires joining through
appointments. Correct SQL:
```sql
SELECT d.specialization,
       ROUND(AVG(t.cost), 2) AS avg_cost
FROM treatments t
JOIN appointments a ON a.id = t.appointment_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.specialization
ORDER BY avg_cost DESC
```

---

### Q13 — Show unpaid invoices

**Expected Behavior:** Filter invoices by Pending or Overdue status

**Generated SQL:**
```sql
SELECT * FROM invoices WHERE status = 'unpaid'
```

**Result:**
```
(0 rows returned — no results)
```

**Status:** ⚠️ Partial

**Notes:** SQL ran without error but returned 0 results because the status values in the
database are `'Pending'` and `'Overdue'`, not `'unpaid'`. The agent used the wrong
status string. Correct SQL:
```sql
SELECT * FROM invoices
WHERE status IN ('Pending', 'Overdue')
```

---

### Q14 — What percentage of appointments are no-shows?

**Expected Behavior:** Percentage calculation using CASE + COUNT

**Generated SQL:**
```sql
SELECT CAST(SUM(CASE WHEN status = 'No-Show' THEN 1 ELSE 0 END) AS REAL)
       * 100 / COUNT(*) FROM appointments
```

**Result:**
```
7.0% of appointments are no-shows.
```

**Status:** ✅ Passed

**Notes:** Correctly calculated the no-show percentage using CASE WHEN. Result of 7.0%
is consistent with the dummy data generated (10% weight given to No-Show status).

---

### Q15 — Show the busiest day of the week for appointments

**Expected Behavior:** Date function to group by day of week

**Generated SQL:**
```sql
SELECT strftime('%w', appointment_date) AS day_of_week,
       COUNT(*) AS appointment_count
FROM appointments
GROUP BY day_of_week
ORDER BY appointment_count DESC
LIMIT 1
```

**Result:**
```
day_of_week | appointment_count
------------|------------------
4           | 78
```

**Status:** ✅ Passed

**Notes:** Correctly used `strftime('%w')` to extract day of week. Result shows day 4
(Wednesday) is the busiest with 78 appointments. Note: `%w` returns 0=Sunday through
6=Saturday, so 4 = Wednesday.

---

### Q16 — Revenue trend by month

**Expected Behavior:** Time series of monthly revenue from invoices

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', invoice_date) AS sales_month,
       SUM(total_amount) AS total_revenue
FROM invoices
GROUP BY sales_month
ORDER BY sales_month
```

**Result:**
```
sales_month | total_revenue
------------|---------------
(13 rows, 2 columns)
```

**Status:** ✅ Passed

**Notes:** Correctly grouped invoices by month and summed revenue. Returned 13 months
of data covering the full dummy data date range.

---

### Q17 — Average appointment duration by doctor

**Expected Behavior:** AVG of duration_minutes from treatments, grouped by doctor

**Generated SQL:**
```sql
SELECT d.name AS doctor_name,
       AVG((julianday(a.end_time) - julianday(a.start_time)) * 24 * 60)
       AS avg_appointment_duration_minutes
FROM appointments a
JOIN doctors d ON a.doctor_id = d.doctor_id
GROUP BY d.name
ORDER BY d.name
```

**Result:**
```
Error executing query: no such column: a.start_time
```

**Status:** ❌ Failed

**Notes:** The agent assumed appointments have `start_time` and `end_time` columns which
do not exist. Duration data is stored in `treatments.duration_minutes`. Correct SQL:
```sql
SELECT d.name,
       ROUND(AVG(t.duration_minutes), 2) AS avg_duration_minutes
FROM treatments t
JOIN appointments a ON a.id = t.appointment_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.id, d.name
ORDER BY d.name
```

---

### Q18 — List patients with overdue invoices

**Expected Behavior:** JOIN patients + invoices, filter by Overdue status

**Generated SQL:**
```sql
SELECT p.first_name || ' ' || p.last_name AS patient_name,
       i.invoice_id, i.invoice_date, i.total_amount,
       i.payment_due_date, i.amount_due
FROM patients p
JOIN invoices i ON p.patient_id = i.patient_id
WHERE i.payment_due_date < date('now')
AND i.payment_status != 'Paid'
```

**Result:**
```
Error executing query: no such column: i.invoice_id
```

**Status:** ❌ Failed

**Notes:** The agent hallucinated multiple columns — `i.invoice_id` (correct is `i.id`),
`i.payment_due_date` (does not exist), `i.amount_due` (does not exist), `i.payment_status`
(correct is `i.status`), and `p.patient_id` (correct is `p.id`). Correct SQL:
```sql
SELECT p.first_name, p.last_name,
       i.invoice_date, i.total_amount, i.status
FROM invoices i
JOIN patients p ON p.id = i.patient_id
WHERE i.status = 'Overdue'
ORDER BY i.total_amount DESC
```

---

### Q19 — Compare revenue between departments

**Expected Behavior:** JOIN invoices through appointments to doctors, GROUP BY department

**Generated SQL:**
```sql
SELECT d.specialization AS department,
       SUM(i.total_amount) AS total_revenue
FROM invoices i
JOIN doctors d ON i.doctor_id = d.doctor_id
GROUP BY d.specialization
ORDER BY total_revenue DESC
```

**Result:**
```
Tool failed: no such column: i.doctor_id
```

**Status:** ❌ Failed

**Notes:** The invoices table has no direct `doctor_id` column — it only has `patient_id`.
To get revenue by department, the query must go through the appointments table to reach
doctors. Correct SQL:
```sql
SELECT d.department,
       ROUND(SUM(i.total_amount), 2) AS total_revenue
FROM invoices i
JOIN appointments a ON a.patient_id = i.patient_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.department
ORDER BY total_revenue DESC
```

---

### Q20 — Show patient registration trend by month

**Expected Behavior:** Groups patients by registration month

**Generated SQL:**
```sql
SELECT strftime('%Y-%m', registration_date) AS registration_month,
       COUNT(patient_id) AS patient_count
FROM patients
GROUP BY registration_month
ORDER BY registration_month
```

**Result:**
```
Error executing query: no such column: registration_date
```

**Status:** ❌ Failed

**Notes:** The agent used `registration_date` but the actual column name in the patients
table is `registered_date`. A very close hallucination — just one character difference
in the column name. Correct SQL:
```sql
SELECT strftime('%Y-%m', registered_date) AS month,
       COUNT(*) AS new_patients
FROM patients
GROUP BY strftime('%Y-%m', registered_date)
ORDER BY month ASC
```

---

## Overall Analysis

### Final Score

| Result | Count | Questions |
|--------|-------|-----------|
| ✅ Passed | 10 | Q1, Q2, Q3, Q4, Q7, Q10, Q11, Q14, Q15, Q16 |
| ⚠️ Partial | 2 | Q9, Q13 |
| ❌ Failed | 8 | Q5, Q6, Q8, Q12, Q17, Q18, Q19, Q20 |
| **Total** | **20** | |

---

### What Worked Well

- Simple single-table queries (COUNT, SUM, GROUP BY) worked perfectly
- Date filtering using `strftime` and `DATE('now', '-N months')` was handled correctly
- HAVING clause queries worked as expected
- Percentage calculations using CASE WHEN were accurate
- The agent gave good natural language summaries for successful queries

### What Failed and Why

**1. Column name hallucinations (most common failure)**
The agent frequently invented column names that do not exist:
- Used `price` / `a.price` instead of `treatments.cost`
- Used `p.name` instead of `p.first_name` / `p.last_name`
- Used `registration_date` instead of `registered_date`
- Used `start_time` / `end_time` instead of `duration_minutes`
- Used `i.invoice_id` instead of `i.id`
- Used `payment_status` instead of `status`

**2. Wrong JOIN paths for revenue queries**
The agent repeatedly tried to join `invoices` directly to `doctors` using a
non-existent `doctor_id` column on invoices. The actual relationship requires
going through the appointments table: `invoices → appointments → doctors`.

**3. Wrong status string values**
For Q13, the agent used `status = 'unpaid'` when the actual values stored are
`'Pending'` and `'Overdue'`.

### Root Cause

The core issue is that the LLM did not have access to the exact database schema
(DDL) during query generation. It guessed column names based on common conventions
rather than reading the actual table definitions. This is a known limitation of
NL2SQL systems without schema injection.

### How I Would Improve the System

1. **Inject DDL into agent memory** — Feed the exact `CREATE TABLE` statements
   as text memory so the agent knows exact column names before generating SQL

2. **Add more targeted seed examples** — Seed Q&A pairs specifically covering
   multi-table JOIN patterns through appointments → invoices → doctors

3. **Add a schema description string** — For example:
   *"Revenue is stored in invoices.total_amount, not in appointments.
   Patient names are in first_name and last_name columns, not name.
   Registration date column is registered_date."*

