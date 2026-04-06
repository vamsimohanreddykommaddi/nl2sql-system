import sqlite3
import random
from datetime import datetime, timedelta

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
DB_NAME = "clinic.db"

# ─────────────────────────────────────────
# DUMMY DATA POOLS
# ─────────────────────────────────────────
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Priya", "Ananya", "Divya", "Meera", "Sneha", "Pooja",
    "Kavya", "Lakshmi", "Nisha", "Riya", "Rahul", "Rohan", "Kiran", "Suresh",
    "Vijay", "Ramesh", "Amit", "Deepak", "Naveen", "Manish", "Sunita", "Geeta",
    "Anjali", "Shweta", "Rekha", "Neha", "Sonia", "Pallavi", "Swathi", "Bhavana",
    "Mohammed", "Abdul", "Imran", "Farhan", "Zaid", "Fatima", "Ayesha", "Zara",
    "Harsha", "Teja", "Lokesh", "Santosh", "Prasad", "Srikanth", "Venkat", "Mahesh",
    "Chandra", "Ashok", "Rajesh", "Suresh", "Uday", "Pavan", "Nikhil", "Tarun",
    "Shruti", "Madhuri", "Revathi", "Sowmya", "Yamini", "Sirisha", "Mounika", "Hema"
]

LAST_NAMES = [
    "Sharma", "Reddy", "Kumar", "Singh", "Patel", "Verma", "Gupta", "Nair",
    "Rao", "Pillai", "Joshi", "Mehta", "Iyer", "Menon", "Bhat", "Hegde",
    "Naidu", "Chowdary", "Murthy", "Raju", "Khan", "Sheikh", "Siddiqui", "Ansari",
    "Desai", "Shah", "Mishra", "Tiwari", "Yadav", "Pandey", "Chauhan", "Dubey",
    "Agarwal", "Bajaj", "Malhotra", "Kapoor", "Chopra", "Bose", "Das", "Ghosh"
]

CITIES = [
    "Hyderabad", "Bangalore", "Chennai", "Mumbai", "Delhi",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"
]

SPECIALIZATIONS = [
    "Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"
]

DEPARTMENTS = {
    "Dermatology": "Skin & Hair",
    "Cardiology": "Heart & Vascular",
    "Orthopedics": "Bone & Joint",
    "General": "General Medicine",
    "Pediatrics": "Child Health"
}

DOCTOR_NAMES = [
    ("Dr. Suresh", "Reddy"), ("Dr. Priya", "Sharma"), ("Dr. Anil", "Kumar"),
    ("Dr. Meena", "Nair"), ("Dr. Rajesh", "Gupta"), ("Dr. Sunita", "Rao"),
    ("Dr. Vikram", "Patel"), ("Dr. Kavitha", "Menon"), ("Dr. Ramesh", "Iyer"),
    ("Dr. Deepa", "Singh"), ("Dr. Harish", "Verma"), ("Dr. Lakshmi", "Pillai"),
    ("Dr. Mohammed", "Khan"), ("Dr. Anjali", "Joshi"), ("Dr. Naveen", "Bhat")
]

TREATMENT_NAMES = {
    "Dermatology": ["Acne Treatment", "Skin Biopsy", "Laser Therapy", "Chemical Peel", "Mole Removal"],
    "Cardiology": ["ECG", "Echocardiogram", "Stress Test", "Angioplasty", "Holter Monitor"],
    "Orthopedics": ["X-Ray", "MRI Scan", "Physiotherapy", "Joint Injection", "Fracture Treatment"],
    "General": ["Blood Test", "Urine Test", "Vaccination", "General Checkup", "BP Monitoring"],
    "Pediatrics": ["Pediatric Checkup", "Vaccination", "Growth Assessment", "Fever Treatment", "Nutrition Counseling"]
}

APPOINTMENT_STATUSES = ["Scheduled", "Completed", "Cancelled", "No-Show"]
INVOICE_STATUSES = ["Paid", "Pending", "Overdue"]
GENDERS = ["M", "F"]


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────
def random_date(start_days_ago=365, end_days_ago=0):
    """Return a random date between start_days_ago and end_days_ago from today."""
    today = datetime.today()
    start = today - timedelta(days=start_days_ago)
    end = today - timedelta(days=end_days_ago)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

def random_datetime(start_days_ago=365, end_days_ago=0):
    """Return a random datetime string."""
    today = datetime.today()
    start = today - timedelta(days=start_days_ago)
    end = today - timedelta(days=end_days_ago)
    delta = end - start
    dt = start + timedelta(
        days=random.randint(0, delta.days),
        hours=random.randint(8, 17),
        minutes=random.choice([0, 15, 30, 45])
    )
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def random_phone():
    """Return a random Indian-style phone number or None."""
    if random.random() < 0.15:   # 15% chance of NULL
        return None
    return f"+91 {random.randint(6,9)}{random.randint(100000000, 999999999)}"

def random_email(first, last):
    """Return a random email or None."""
    if random.random() < 0.20:   # 20% chance of NULL
        return None
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    num = random.randint(1, 999)
    return f"{first.lower()}.{last.lower()}{num}@{random.choice(domains)}"


# ─────────────────────────────────────────
# STEP 1 — CREATE SCHEMA
# ─────────────────────────────────────────
def create_tables(cur):
    print("Creating tables...")

    cur.executescript("""
        DROP TABLE IF EXISTS invoices;
        DROP TABLE IF EXISTS treatments;
        DROP TABLE IF EXISTS appointments;
        DROP TABLE IF EXISTS doctors;
        DROP TABLE IF EXISTS patients;

        CREATE TABLE patients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name      TEXT NOT NULL,
            last_name       TEXT NOT NULL,
            email           TEXT,
            phone           TEXT,
            date_of_birth   DATE,
            gender          TEXT,
            city            TEXT,
            registered_date DATE
        );

        CREATE TABLE doctors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            specialization  TEXT,
            department      TEXT,
            phone           TEXT
        );

        CREATE TABLE appointments (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id        INTEGER,
            doctor_id         INTEGER,
            appointment_date  DATETIME,
            status            TEXT,
            notes             TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
        );

        CREATE TABLE treatments (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id    INTEGER,
            treatment_name    TEXT,
            cost              REAL,
            duration_minutes  INTEGER,
            FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        );

        CREATE TABLE invoices (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id    INTEGER,
            invoice_date  DATE,
            total_amount  REAL,
            paid_amount   REAL,
            status        TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );
    """)
    print("  ✓ All tables created.")


# ─────────────────────────────────────────
# STEP 2 — INSERT DUMMY DATA
# ─────────────────────────────────────────

def insert_doctors(cur):
    print("Inserting doctors...")
    doctors = []
    # 3 doctors per specialization = 15 total
    spec_cycle = []
    for spec in SPECIALIZATIONS:
        spec_cycle.extend([spec] * 3)

    for i, (first, last) in enumerate(DOCTOR_NAMES):
        spec = spec_cycle[i]
        dept = DEPARTMENTS[spec]
        name = f"{first} {last}"
        phone = random_phone() or f"+91 9{random.randint(100000000, 999999999)}"
        doctors.append((name, spec, dept, phone))

    cur.executemany(
        "INSERT INTO doctors (name, specialization, department, phone) VALUES (?, ?, ?, ?)",
        doctors
    )
    print(f"  ✓ Inserted {len(doctors)} doctors.")
    return len(doctors)


def insert_patients(cur):
    print("Inserting patients...")
    patients = []
    for _ in range(200):
        first = random.choice(FIRST_NAMES)
        last  = random.choice(LAST_NAMES)
        dob   = random_date(start_days_ago=365*60, end_days_ago=365*5)  # age 5–60
        patients.append((
            first,
            last,
            random_email(first, last),
            random_phone(),
            dob,
            random.choice(GENDERS),
            random.choice(CITIES),
            random_date(start_days_ago=730, end_days_ago=0)
        ))

    cur.executemany("""
        INSERT INTO patients
            (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, patients)
    print(f"  ✓ Inserted {len(patients)} patients.")
    return len(patients)


def insert_appointments(cur):
    print("Inserting appointments...")

    # Make some patients visit more (repeat visitors)
    # Patients 1–30 are "frequent" — get weighted selection
    patient_ids = list(range(1, 201))
    weights = []
    for pid in patient_ids:
        if pid <= 30:
            weights.append(8)   # frequent visitors
        elif pid <= 80:
            weights.append(3)   # occasional
        else:
            weights.append(1)   # rare

    # Doctors 1–5 are busier
    doctor_ids = list(range(1, 16))
    doc_weights = [10, 9, 8, 8, 7, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1]

    appointments = []
    notes_options = [
        "Follow-up required", "Routine checkup", "Emergency visit",
        "Patient reported improvement", "Referred by another doctor", None, None, None
    ]

    for _ in range(500):
        pid    = random.choices(patient_ids, weights=weights)[0]
        did    = random.choices(doctor_ids,  weights=doc_weights)[0]
        dt     = random_datetime(start_days_ago=365, end_days_ago=0)
        status = random.choices(
            APPOINTMENT_STATUSES,
            weights=[15, 55, 20, 10]   # more Completed, fewer No-Show
        )[0]
        note = random.choice(notes_options)
        appointments.append((pid, did, dt, status, note))

    cur.executemany("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
    """, appointments)
    print(f"  ✓ Inserted {len(appointments)} appointments.")
    return len(appointments)


def insert_treatments(cur):
    print("Inserting treatments...")

    # Get completed appointment IDs with their doctor's specialization
    cur.execute("""
        SELECT a.id, d.specialization
        FROM appointments a
        JOIN doctors d ON d.id = a.doctor_id
        WHERE a.status = 'Completed'
    """)
    completed = cur.fetchall()

    # Pick 350 of them (or all if fewer)
    selected = random.sample(completed, min(350, len(completed)))

    treatments = []
    for appt_id, spec in selected:
        tname    = random.choice(TREATMENT_NAMES.get(spec, ["General Procedure"]))
        cost     = round(random.uniform(50, 5000), 2)
        duration = random.randint(10, 120)
        treatments.append((appt_id, tname, cost, duration))

    cur.executemany("""
        INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
        VALUES (?, ?, ?, ?)
    """, treatments)
    print(f"  ✓ Inserted {len(treatments)} treatments.")
    return len(treatments)


def insert_invoices(cur):
    print("Inserting invoices...")

    # Get all patient IDs
    cur.execute("SELECT id FROM patients")
    all_pids = [row[0] for row in cur.fetchall()]

    # Pick 300 patients (with repetition allowed — patients can have multiple invoices)
    invoices = []
    for _ in range(300):
        pid          = random.choice(all_pids)
        inv_date     = random_date(start_days_ago=365, end_days_ago=0)
        total        = round(random.uniform(100, 8000), 2)
        status       = random.choices(
            INVOICE_STATUSES,
            weights=[55, 30, 15]   # mostly Paid
        )[0]

        if status == "Paid":
            paid = total
        elif status == "Pending":
            paid = round(random.uniform(0, total * 0.5), 2)
        else:  # Overdue
            paid = round(random.uniform(0, total * 0.3), 2)

        invoices.append((pid, inv_date, total, paid, status))

    cur.executemany("""
        INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
        VALUES (?, ?, ?, ?, ?)
    """, invoices)
    print(f"  ✓ Inserted {len(invoices)} invoices.")
    return len(invoices)


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("=" * 50)
    print("  Clinic Database Setup")
    print("=" * 50)

    conn = sqlite3.connect(DB_NAME)
    cur  = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON")

    create_tables(cur)
    conn.commit()

    n_doctors      = insert_doctors(cur)    
    conn.commit()
    n_patients     = insert_patients(cur)   
    conn.commit()
    n_appointments = insert_appointments(cur) 
    conn.commit()
    n_treatments   = insert_treatments(cur) 
    conn.commit()
    n_invoices     = insert_invoices(cur)  
    conn.commit()

    conn.close()

    print()
    print("=" * 50)
    print("  ✅ Database setup complete!")
    print(f"  📁 File created : {DB_NAME}")
    print(f"  👨‍⚕️ Doctors       : {n_doctors}")
    print(f"  🧑‍🤝‍🧑 Patients      : {n_patients}")
    print(f"  📅 Appointments  : {n_appointments}")
    print(f"  💊 Treatments    : {n_treatments}")
    print(f"  🧾 Invoices      : {n_invoices}")
    print("=" * 50)


if __name__ == "__main__":
    main()