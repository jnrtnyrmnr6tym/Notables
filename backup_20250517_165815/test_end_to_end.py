import os
import requests
import json
import time
from dotenv import load_dotenv

TOKEN = "Bq3YFeKqHkUzZGs8HFhoUFfaGs258keoeGXGoarEW4S2"
API_BASE = "http://localhost:5000"
REPORT_FILE = "test_report.txt"

load_dotenv()

report_lines = []

def log(msg):
    print(msg)
    report_lines.append(msg)

def test_cookies():
    log("\n== Checking cookies ==")
    res = os.system("python token_monitor_with_notable_check.py --test > test_cookies_output.txt")
    with open("test_cookies_output.txt", "r", encoding="utf-8", errors="replace") as f:
        output = f.read()
    log(output)
    return "Cookies are valid." in output or "Las cookies son válidas." in output

def process_token():
    log(f"\n== Processing real token: {TOKEN} ==")
    res = os.system(f"python token_monitor_with_notable_check.py --token {TOKEN} > test_process_token_output.txt")
    with open("test_process_token_output.txt", "r", encoding="utf-8", errors="replace") as f:
        output = f.read()
    log(output)
    return True

def check_api():
    log(f"\n== Querying internal API for the token ==")
    url = f"{API_BASE}/api/token/{TOKEN}"
    try:
        resp = requests.get(url)
        log(f"GET {url} -> {resp.status_code}")
        log(resp.text)
        return resp.status_code == 200
    except Exception as e:
        log(f"Error querying API: {e}")
        return False

def check_approved_tokens():
    log("\n== Checking if the token is in approved_tokens.json ==")
    try:
        with open("approved_tokens.json", "r", encoding="utf-8", errors="replace") as f:
            tokens = json.load(f)
        found = any(t.get("token_address") == TOKEN for t in tokens)
        log(f"Is token approved?: {'YES' if found else 'NO'}")
        return found
    except Exception as e:
        log(f"Error reading approved_tokens.json: {e}")
        return False

def show_last_logs():
    log("\n== Last events from the main log ==")
    try:
        with open("token_monitor.log", "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-30:]
        for line in lines:
            log(line.rstrip())
    except Exception as e:
        log(f"Error reading token_monitor.log: {e}")

def main():
    ok_cookies = test_cookies()
    if not ok_cookies:
        log("[ERROR] Cookies are not valid. Stopping test.")
        return
    process_token()
    time.sleep(3)  # Wait for processing to finish
    check_api()
    check_approved_tokens()
    show_last_logs()
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    log(f"\n== Report saved to {REPORT_FILE} ==")

if __name__ == "__main__":
    main() 