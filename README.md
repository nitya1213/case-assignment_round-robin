# :rocket: Case Assignment Bot
The Case Assignment Bot is an automation tool that assigns open cases to active employees using a round-robin algorithm, updates a Google Sheet, and sends an email notification to each assigned employee.
It is designed for lightweight support operations, helpdesks, and customer service teams that track their cases in Google Sheets.
---
## :drawing_pin: Key Features
* **Round-robin case assignment**
* **Google Sheets as the data source**
* **Google Apps Script Web App as the API**
* **Auto-updates assignments in Google Sheets**
* **Email notifications sent automatically**
* **Simple configuration using a `.env` file**
* **Runs via Python or a bundled `run.sh` helper script**
---
## :hammer_and_spanner: How It Works
The system uses three components working together:
### :one: Google Sheets
Two sheets inside the same spreadsheet:
* **Roster**
  Contains employee list + email + active status
* **Case Tracker**
  Contains cases that may be Open/Closed + optional Assignee field
### :two: Google Apps Script Web App
Acts as a tiny backend API that:
* Returns sheet data as JSON (`GET`)
* Accepts updates for assigned cases (`POST`)
### :three: Python Script
Fetches data from the Web App and:
* Finds all active employees
* Finds unassigned open cases
* Assigns them fairly (round-robin)
* Sends email notifications
* Pushes assigned values back to Google Sheets
---
## :cog: Project Structure
```
case-assignment-bot/
├── assign_cases.py     # Main logic
├── run.sh              # Helper script for running the bot
├── requirements.txt    # Python dependencies
├── .env                # API URL + email credentials
└── .gitignore
```
---
## :spanner: Configuration
Place your configuration inside `.env`:
```
GOOGLE_WEB_APP_URL=https://script.google.com/macros/s/xxxx/exec
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```
### Required:
* **GOOGLE_WEB_APP_URL**: URL of your deployed Apps Script Web App
* **SENDER_EMAIL**: Gmail/O365/SMTP-compatible email
* **SENDER_PASSWORD**: App password (not your real login password)
---
## :arrow_forwards: Running the Bot
You can run the bot with a single command.
### **Option 1 — Using the helper script (recommended)**
```
./run.sh
```
(If needed: `chmod +x run.sh`)
This script will:
* Activate/create virtual environment
* Install dependencies
* Validate `.env`
* Run `assign_cases.py`
### **Option 2 — Running Python directly**
```
source venv/bin/activate
python assign_cases.py
```
---
## :outbox_tray: What Happens When You Run It
### :heavy_tick: Fetches roster and cases
The bot retrieves:
* All employees
* All cases
from Google Sheets via your Web App.
### :heavy_tick: Filters relevant data
It selects:
* Active employees (`Active = Yes`)
* Open cases without an assignee
### :heavy_tick: Assigns cases
Cases are distributed evenly using a **round-robin algorithm**.
### :heavy_tick: Updates Google Sheets
Each assigned case is written back into the **Assignee** column.
### :heavy_tick: Sends email notifications
Each employee gets an email with:
* Case Number
* Subject
* Basic details
---
## :chart_with_upwards_trend: Example Output (Console)
```
Fetching roster...
Found 3 active employees.
Fetching case tracker...
Unassigned cases: 2
Assigning 1001 → Alice
Assigning 1002 → Bob
Updating assignments...
{'status': 'ok', 'updated': 2}
Done.
```
---
## :bar_chart: Example Result (Google Sheets)
Before:
| CaseNumber | Status | Assignee |
| ---------- | ------ | -------- |
| 1001       | Open   |          |
| 1002       | Open   |          |


After:
| CaseNumber | Status | Assignee                                      |
| ---------- | ------ | --------------------------------------------- |
| 1001       | Open   | [alice@example.com](mailto:alice@example.com) |
| 1002       | Open   | [bob@example.com](mailto:bob@example.com)     |
---
## :insect: Troubleshooting
### :x: 500 Internal Server Error
Your `GOOGLE_WEB_APP_URL` is incorrect or the Apps Script deployment is wrong.
### :x: No emails received
You must use an **app password**, not a normal login password.
### :x: “ScriptError: Access denied”
Your Web App must be deployed with:
**Who has access:** Anyone
---
## :page_facing_up: License
MIT License — free for personal and commercial use.
