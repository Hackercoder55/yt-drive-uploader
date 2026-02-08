from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import gspread
import time

FOLDER_ID = "1bnIK1Ls8g6vJ-mdbRmwNflpBQTu6mqhs"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1P-_ljZFeGteadqIiPX0_rXj3NWRLxJcHcOGoxVms2WU/edit?gid=0#gid=0"

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(SHEET_URL).sheet1

results = drive.files().list(
    q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
    fields="files(id, name, webViewLink)",
    pageSize=1000
).execute()

files = results.get("files", [])
print("Found:", len(files), "videos")

rows = []
for f in files:
    rows.append([
        f["id"],
        f["name"],
        f["webViewLink"],
        "",          # Title
        "Pending",
        "", "", ""
    ])

# 🔥 Batch insert (100 rows at a time)
BATCH_SIZE = 100
for i in range(0, len(rows), BATCH_SIZE):
    chunk = rows[i:i + BATCH_SIZE]
    sheet.append_rows(chunk)
    print(f"Inserted rows {i+1} to {i+len(chunk)}")
    time.sleep(2)  # avoid quota

print("Done ✅")
