from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import gspread
import time

# ---------------- CONFIG ----------------
FOLDER_ID = "1bnIK1Ls8g6vJ-mdbRmwNflpBQTu6mqhs"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1P-_ljZFeGteadqIiPX0_rXj3NWRLxJcHcOGoxVms2WU/edit?gid=0#gid=0"

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]

TITLES = [
    "Your Videos Deserve Better Editing",
    "I Turn Raw Clips Into Scroll-Stopping Videos",
    "Need a Video Editor? I Help Creators Grow",
    "This Is What a Professional Video Editor Can Do"
]

DESCRIPTION = (
    "Struggling to get views or engagement?\n\n"
    "I help creators and brands turn raw footage into clean, "
    "high-retention videos.\n\n"
    "🌐 https://theeditimation.in\n"
    "📧 queries.santosh@gmail.com\n"
    "📱 WhatsApp: +91 6205789970"
)

HASHTAGS = (
    "#VideoEditor #VideoEditing #ContentCreator #YouTuber "
    "#ReelsEditor #ShortsEditor #GrowOnYouTube "
    "#CreativeAgency #FreelancerLife"
)
# ----------------------------------------

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES
)

drive = build("drive", "v3", credentials=creds)
gc = gspread.authorize(creds)
sheet = gc.open_by_url(SHEET_URL).sheet1

# 🔥 STEP 1: Clear sheet completely
sheet.clear()

# 🔥 STEP 2: Add headers (ONE ROW)
headers = [
    "File ID", "File Name", "Drive Link", "Title", "Status",
    "Upload Date", "Upload Time", "YouTube Link",
    "Description", "Hashtags"
]
sheet.append_row(headers)

# 🔥 STEP 3: Fetch ALL videos (with pagination)
all_files = []
page_token = None

while True:
    response = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="nextPageToken, files(id, name, webViewLink)",
        pageSize=1000,
        pageToken=page_token
    ).execute()

    all_files.extend(response.get("files", []))
    page_token = response.get("nextPageToken")

    if not page_token:
        break

print(f"Total videos found: {len(all_files)}")

# 🔥 STEP 4: Prepare rows (CLEAN & ORDERED)
rows = []
for i, f in enumerate(all_files):
    rows.append([
        f["id"],                          # A File ID
        f["name"],                        # B File Name
        f["webViewLink"],                 # C Drive Link
        TITLES[i % len(TITLES)],          # D Title (loop)
        "Pending",                        # E Status
        "",                               # F Upload Date
        "",                               # G Upload Time
        "",                               # H YouTube Link
        DESCRIPTION,                      # I Description
        HASHTAGS                          # J Hashtags
    ])

# 🔥 STEP 5: Batch insert (NO LADDER)
BATCH_SIZE = 100
for i in range(0, len(rows), BATCH_SIZE):
    chunk = rows[i:i + BATCH_SIZE]
    sheet.append_rows(chunk, value_input_option="RAW")
    print(f"Inserted rows {i+1} to {i+len(chunk)}")
    time.sleep(2)

print("✅ Sheet generated cleanly. No ladder. Done.")
