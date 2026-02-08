import gspread
from google.oauth2.service_account import Credentials
import time

# ---------- CONFIG ----------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1P-_ljZFeGteadqIiPX0_rXj3NWRLxJcHcOGoxVms2WU/edit?gid=0#gid=0"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

TITLES = [
    "Your Videos Deserve Better Editing | Professional Video Editor for Creators & Brands",
    "I Turn Raw Clips Into Scroll-Stopping Videos | Video Editing Services",
    "Need a Video Editor? I Help Creators & Brands Grow With Clean Edits",
    "This Is What a Professional Video Editor Can Do for Your Content"
]

DESCRIPTION = """Struggling to get views or engagement?

I help creators and brands turn raw footage into clean, high-retention videos.

🌐 https://theeditimation.in
📧 queries.santosh@gmail.com
📱 WhatsApp: +91 6205789970
"""

HASHTAGS = (
    "#VideoEditor #VideoEditing #ContentCreator #YouTuber "
    "#ReelsEditor #ShortsEditor #GrowOnYouTube "
    "#CreativeAgency #FreelancerLife"
)

# ----------------------------

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)
sheet = gc.open_by_url(SHEET_URL).sheet1

rows = sheet.get_all_values()

updates = []
title_index = 0

for row_num in range(1, len(rows)):  # skip header
    row = rows[row_num]

    drive_link = row[2] if len(row) > 2 else ""
    title = row[3] if len(row) > 3 else ""
    status = row[4] if len(row) > 4 else ""

    if drive_link and (status == "" or status.lower() == "pending") and title == "":
        assigned_title = TITLES[title_index % len(TITLES)]
        title_index += 1

        updates.append({
            "range": f"D{row_num+1}",
            "values": [[assigned_title]]
        })
        updates.append({
            "range": f"I{row_num+1}",
            "values": [[DESCRIPTION]]
        })
        updates.append({
            "range": f"J{row_num+1}",
            "values": [[HASHTAGS]]
        })

# 🔥 Batch update (quota safe)
if updates:
    sheet.batch_update(updates)
    print(f"Updated {len(updates)//3} rows successfully ✅")
else:
    print("No rows to update.")

time.sleep(1)
