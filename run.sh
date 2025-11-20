#!/usr/bin/env bash
#
# run.sh – helper script to run the Case Assignment Bot
# Usage:
#   chmod +x run.sh
#   ./run.sh

set -euo pipefail

### 1) Go to the directory where this script lives

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "➡ Project directory: $SCRIPT_DIR"

### 2) Check for Python 3

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install it first (e.g. sudo apt install python3)."
  exit 1
fi

### 3) Create virtual environment if it doesn't exist

if [ ! -d "venv" ]; then
  echo "📦 No virtual environment found. Creating one at ./venv ..."
  python3 -m venv venv
  echo "✅ Virtual environment created."
fi

### 4) Activate virtual environment

# shellcheck disable=SC1091
source "venv/bin/activate"
echo "✅ Virtual environment activated."

### 5) Install dependencies from requirements.txt

if [ -f "requirements.txt" ]; then
  echo "📚 Installing dependencies from requirements.txt ..."
  pip install -r requirements.txt
  echo "✅ Dependencies installed (or already up to date)."
else
  echo "⚠️ requirements.txt not found. Skipping dependency install."
fi

### 6) Check for .env file

if [ ! -f ".env" ]; then
  cat <<EOF
❌ .env file not found.

Create a .env file in this folder with at least:

GOOGLE_WEB_APP_URL=https://script.google.com/macros/s/XXXXXXXX/exec
SENDER_EMAIL=yourgmail@gmail.com
SENDER_PASSWORD=your_gmail_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

Then re-run: ./run.sh
EOF
  exit 1
fi

# Optional sanity check: warn if URL still has placeholder
if grep -q "XXXX" .env; then
  echo "⚠️ WARNING: Your GOOGLE_WEB_APP_URL still contains 'XXXX'."
  echo "   Edit .env and paste the REAL Web App URL from Apps Script."
fi

### 7) Run the Python script

if [ ! -f "assign_cases.py" ]; then
  echo "❌ assign_cases.py not found in $SCRIPT_DIR"
  exit 1
fi

echo "🚀 Running case assignment script..."
python assign_cases.py
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Script finished successfully."
else
  echo "❌ Script exited with code $EXIT_CODE."
fi

exit $EXIT_CODE
