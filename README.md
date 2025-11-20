Absolutely — here is a **complete, production-ready README.md** that includes **EVERYTHING** you need:

* directory structure
* installation
* Google Sheets setup
* Apps Script setup
* Python setup
* how to run
* what output looks like
* troubleshooting

You can **copy–paste this entire thing** into a README.md file.

---

# README.md

# 🚀 Case Assignment Automation System

Automated case assignment + email notification system using **Google Sheets**, **Google Apps Script**, and **Python**.

---

# 📌 Overview

This project automates a customer support workflow:

1. **Fetch employee roster** from Google Sheets
2. **Fetch open cases** from Google Sheets
3. **Assign unassigned open cases** using a **round-robin algorithm**
4. **Update assignments back into Google Sheets**
5. **Send an email notification** to each employee assigned a new case

It uses:

* **Google Apps Script Web App** = API endpoint
* **Google Sheets** = data store
* **Python Script** = processing + email sending

---

# 📁 Directory Structure

Create the following directory:

```
case-assignment-bot/
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── assign_cases.py       # Main script
```

---

# 🛠️ Installation (Ubuntu 24)

## 1. Install Python + Tools

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

## 2. Create Project Folder

```bash
mkdir -p ~/case-assignment-bot
cd ~/case-assignment-bot
```

## 3. Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Create `requirements.txt`

```bash
cat > requirements.txt << 'EOF'
requests
python-dotenv
EOF
```

Install packages:

```bash
pip install -r requirements.txt
```

---

# 🧾 Google Sheets Setup

Open Google Sheets and create a new spreadsheet.

## 1. Create **Roster** Sheet

Rename Sheet1 → `Roster`

Header row:

| Employee Name | Email | Active |
| ------------- | ----- | ------ |

Example rows:

| Employee Name | Email                                     | Active |
| ------------- | ----------------------------------------- | ------ |
| Alice         | [alice@email.com](mailto:alice@email.com) | Yes    |
| Bob           | [bob@email.com](mailto:bob@email.com)     | Yes    |
| Carol         | [carol@email.com](mailto:carol@email.com) | No     |

---

## 2. Create **Case Tracker** Sheet

Add a new sheet → rename to **Case Tracker**

| Id | CaseNumber | CreatedDate | Subject | Priority | Status | Assignee |
| -- | ---------- | ----------- | ------- | -------- | ------ | -------- |

Example:

| Id | CaseNumber | Status | Assignee |
| -- | ---------- | ------ | -------- |
| 1  | 1001       | Open   |          |
| 2  | 1002       | Open   |          |
| 3  | 1003       | Closed |          |

---

## 3. Copy Your Sheet ID

URL format:

```
https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit#gid=0
```

Copy only the `<SHEET_ID>`.

---

# 🟦 Google Apps Script Web App (Backend API)

This script allows Python to read/write the Google Sheet.

---

## 1. Open Apps Script

Inside your Google Sheet:

`Extensions → Apps Script`

Delete all code and paste this:

```javascript
const SHEET_ID = 'YOUR_SHEET_ID_HERE';

function doGet(e) {
  try {
    const sheetName = e.parameter.sheet;
    if (!sheetName) return asJson_({ error: 'Missing sheet parameter' });

    const ss = SpreadsheetApp.openById(SHEET_ID);
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return asJson_({ error: 'Sheet not found: ' + sheetName });

    const data = sheet.getDataRange().getValues();
    return asJson_(data);

  } catch (err) {
    return asJson_({ error: err.toString() });
  }
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || '{}');
    const action = body.action;

    const ss = SpreadsheetApp.openById(SHEET_ID);

    if (action === 'updateAssignments') {
      const sheet = ss.getSheetByName('Case Tracker');
      if (!sheet) return asJson_({ error: 'Case Tracker not found' });

      const data = sheet.getDataRange().getValues();
      const header = data[0];
      const assigneeCol = header.indexOf('Assignee') + 1;

      if (!assigneeCol) return asJson_({ error: 'Assignee column missing' });

      const updates = body.updates || [];
      updates.forEach(u => {
        sheet.getRange(u.row, assigneeCol).setValue(u.assignee);
      });

      return asJson_({ status: 'ok', updated: updates.length });
    }

    return asJson_({ error: 'Unknown action' });

  } catch (err) {
    return asJson_({ error: err.toString() });
  }
}

function asJson_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
```

### Replace:

```javascript
const SHEET_ID = 'YOUR_SHEET_ID_HERE';
```

with your actual Sheet ID.

---

## 2. Deploy Web App

Go to:

* **Deploy → New Deployment**
* Select type: **Web App**
* Execute As: **Me**
* Who has access: **Anyone**
* Click **Deploy**
* Copy the generated **Web App URL**

Example:

```
https://script.google.com/macros/s/AKfycbx.../exec
```

---

# 🔐 Create `.env` File

Inside your project folder:

```bash
cat > .env << 'EOF'
GOOGLE_WEB_APP_URL=https://script.google.com/macros/s/XXXXX/exec
SENDER_EMAIL=yourgmail@gmail.com
SENDER_PASSWORD=your_gmail_app_password  # NOT your real password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EOF
```

---

# 🐍 Python Script (`assign_cases.py`)

Create the file:

```bash
nano assign_cases.py
```

Paste this entire script:

```python
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
    response = requests.get(WEB_APP_URL, params={"sheet": sheet_name})
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(data["error"])
    return data


def update_assignments(updates):
    payload = {"action": "updateAssignments", "updates": updates}
    response = requests.post(WEB_APP_URL, json=payload)
    response.raise_for_status()
    return response.json()


def send_email(to_email, case_number, subject):
    msg = MIMEText(
        f"You have been assigned a new case.\n\nCase: {case_number}\nSubject: {subject}"
    )
    msg["Subject"] = f"New Case Assigned: {case_number}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


def to_dict(rows):
    header = rows[0]
    return header, [dict(zip(header, row)) for row in rows[1:]]


def main():
    print("Fetching roster...")
    roster_raw = fetch_sheet("Roster")
    header, roster = to_dict(roster_raw)

    active = [r for r in roster if str(r.get("Active", "")).lower() == "yes"]

    print("Fetching cases...")
    case_raw = fetch_sheet("Case Tracker")
    chead, cases = to_dict(case_raw)

    unassigned = []
    for i, case in enumerate(cases, start=2):
        if case["Status"].lower() == "open" and case["Assignee"] == "":
            unassigned.append((i, case))

    cycle = itertools.cycle(active)
    updates = []

    for row, case in unassigned:
        employee = next(cycle)
        email = employee["Email"]

        print(f"Assigning {case['CaseNumber']} → {employee['Employee Name']}")

        updates.append({"row": row, "assignee": email})
        send_email(email, case["CaseNumber"], case["Subject"])

    if updates:
        print("Pushing updates to Google Sheets...")
        print(update_assignments(updates))
    else:
        print("No unassigned cases.")


if __name__ == "__main__":
    main()
```

---

# ▶️ How to Run

From your project folder:

```bash
cd ~/case-assignment-bot
source venv/bin/activategi
python assign_cases.py
```

---

# ✔️ Expected Output

Terminal will show:

```
Fetching roster...
Fetching cases...
Assigning 1001 → Alice
Assigning 1002 → Bob
Pushing updates to Google Sheets...
{'status': 'ok', 'updated': 2}
```

---

# 📊 What You Should See in Google Sheets

### Before running:

| CaseNumber | Status | Assignee |
| ---------- | ------ | -------- |
| 1001       | Open   |          |
| 1002       | Open   |          |

### After running:

| CaseNumber | Status | Assignee                                  |
| ---------- | ------ | ----------------------------------------- |
| 1001       | Open   | [alice@email.com](mailto:alice@email.com) |
| 1002       | Open   | [bob@email.com](mailto:bob@email.com)     |

---

# 📧 Email Notifications

Each assigned employee receives:

**Subject:**
`New Case Assigned: 1001`

**Body:**

```
You have been assigned a new case.

Case: 1001
Subject: Login issue
```

---

# ❗ Troubleshooting

### ❌ Python shows

`500 Internal Server Error`

➡️ Your `.env` still uses the placeholder URL:
`https://script.google.com/macros/s/XXXX/exec`

Fix by pasting the real Web App URL.

---

### ❌ Browser shows

`ScriptError: Access denied`

Fix:

Apps Script → Deploy → Manage deployments →
Set *Who has access* to: **Anyone**

---

### ❌ No emails are received

Gmail requires an **App Password**.

Follow this:

1. Enable 2-Step Verification
2. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Generate an app password
4. Put it into `.env`

---

# 🎯 Done!

You now have a fully functional automation system:

* Google Sheets backend
* Apps Script API
* Python assignment engine
* Email notification system

If you want, I can also create:

✅ A visual architecture diagram
✅ A cron job automation guide
✅ A GUI dashboard
✅ Docker version of the project

Just tell me!

