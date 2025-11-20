import os
import itertools
import requests
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

WEB_APP_URL = os.getenv("GOOGLE_WEB_APP_URL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


def fetch_sheet(sheet_name):
    """Fetch a sheet as a 2D list using the Apps Script Web App."""
    resp = requests.get(WEB_APP_URL, params={"sheet": sheet_name})
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"Error from web app: {data['error']}")
    return data  # list of lists


def update_assignments(updates):
    """
    Send assignment updates back to Apps Script.
    'updates' is a list of dicts like {"row": 2, "assignee": "alice@example.com"}.
    """
    payload = {
        "action": "updateAssignments",
        "updates": updates,
    }
    resp = requests.post(WEB_APP_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and data.get("status") != "ok":
        raise RuntimeError(f"Error updating assignments: {data}")
    return data


def send_email(to_email, case_number, subject):
    """Send an email notification about a new case assignment."""
    body = (
        f"Hi,\n\n"
        f"You have been assigned a new case.\n\n"
        f"Case Number: {case_number}\n"
        f"Subject: {subject}\n\n"
        f"Please log into the system and start working on it.\n\n"
        f"Thanks."
    )

    msg = MIMEText(body)
    msg["Subject"] = f"New Case Assigned: {case_number}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


def build_dict_rows(raw_rows):
    """Convert 2D list [header, row1, row2, ...] into list of dicts."""
    header = raw_rows[0]
    dict_rows = []
    for row in raw_rows[1:]:
        d = dict(zip(header, row))
        dict_rows.append(d)
    return header, dict_rows


def main():
    print("Fetching roster...")
    roster_raw = fetch_sheet("Roster")
    roster_header, roster = build_dict_rows(roster_raw)
    print(f"Found {len(roster)} employees.")

    # Filter active employees
    active_employees = [
        r for r in roster if str(r.get("Active", "")).strip().lower() == "yes"
    ]
    if not active_employees:
        print("No active employees found. Exiting.")
        return

    print(f"Active employees: {[e['Employee Name'] for e in active_employees]}")

    print("Fetching case tracker...")
    cases_raw = fetch_sheet("Case Tracker")
    cases_header, cases = build_dict_rows(cases_raw)
    print(f"Found {len(cases)} cases (including closed ones).")

    # Identify unassigned open cases
    unassigned_cases = []
    for index, case in enumerate(cases, start=2):  # start=2 because row 1 is header
        status = str(case.get("Status", "")).strip().lower()
        assignee = str(case.get("Assignee", "")).strip()
        if status == "open" and assignee == "":
            unassigned_cases.append((index, case))  # (sheet_row_index, case_dict)

    if not unassigned_cases:
        print("No unassigned open cases. Nothing to do.")
        return

    print(f"Unassigned open cases: {len(unassigned_cases)}")

    # Round-robin assignment
    cycle = itertools.cycle(active_employees)
    updates = []

    for sheet_row, case in unassigned_cases:
        employee = next(cycle)
        assignee_email = employee["Email"]
        case_number = case.get("CaseNumber", "")
        subject = case.get("Subject", "")

        print(
            f"Assigning case {case_number} ('{subject}') "
            f"to {employee['Employee Name']} <{assignee_email}> "
            f"at sheet row {sheet_row}"
        )

        updates.append({
            "row": sheet_row,
            "assignee": assignee_email,
        })

        # Send email notification
        send_email(assignee_email, case_number, subject)

    # Push updates to Google Sheets
    print("Updating assignments in Google Sheets...")
    result = update_assignments(updates)
    print("Update result:", result)
    print("Done.")


if __name__ == "__main__":
    main()
