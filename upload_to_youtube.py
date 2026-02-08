import io
import os
import pickle
import datetime
import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# --------- CREATE CREDS FILES FROM ENV ---------
if not os.path.exists("service_account.json"):
    with open("service_account.json", "w") as f:
        f.write(os.environ["SERVICE_ACCOUNT_JSON"])

if not os.path.exists("client_secret.json"):
    with open("client_secret.json", "w") as f:
        f.write(os.environ["CLIENT_SECRET_JSON"])
# ================= CONFIG =================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1P-_ljZFeGteadqIiPX0_rXj3NWRLxJcHcOGoxVms2WU/edit#gid=0"

SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets"]
SCOPES_DRIVE = ["https://www.googleapis.com/auth/drive.readonly"]
SCOPES_YT = ["https://www.googleapis.com/auth/youtube.upload"]

TOKEN_FILE = "yt_token.pickle"
# =========================================


# -------- Google Sheets (Service Account) --------
sheet_creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES_SHEETS
)
gc = gspread.authorize(sheet_creds)
sheet = gc.open_by_url(SHEET_URL).sheet1


# -------- Google Drive (Service Account) --------
drive_creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES_DRIVE
)
drive = build("drive", "v3", credentials=drive_creds)


# -------- YouTube OAuth (Saved Token) --------
yt_creds = None

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "rb") as token:
        yt_creds = pickle.load(token)

if not yt_creds or not yt_creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        SCOPES_YT
    )
    yt_creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(yt_creds, token)

youtube = build("youtube", "v3", credentials=yt_creds)


# -------- Read Sheet --------
rows = sheet.get_all_values()

for idx in range(1, len(rows)):  # skip header
    row = rows[idx]

    drive_link = row[2]      # C
    title = row[3]           # D
    status = row[4]          # E
    description = row[8]     # I
    hashtags = row[9]        # J

    if status == "Pending" and drive_link and title:
        print("Uploading:", title)

        # -------- Extract Drive File ID --------
        file_id = drive_link.split("/d/")[1].split("/")[0]

        # -------- Download Video --------
        request = drive.files().get_media(fileId=file_id)
        fh = io.FileIO("video.mp4", "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        # -------- Upload to YouTube --------
        upload_request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": f"{description}\n\n{hashtags}",
                    "categoryId": "22"
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=MediaFileUpload("video.mp4", resumable=True)
        )

        response = upload_request.execute()

        # -------- Update Sheet --------
        now = datetime.datetime.now()

        sheet.update(values=[["Uploaded"]], range_name=f"E{idx+1}")
        sheet.update(values=[[now.strftime("%Y-%m-%d")]], range_name=f"F{idx+1}")
        sheet.update(values=[[now.strftime("%H:%M")]], range_name=f"G{idx+1}")
        sheet.update(
            values=[[f"https://www.youtube.com/watch?v={response['id']}"]],
            range_name=f"H{idx+1}"
        )

        print("✅ Uploaded & sheet updated successfully")
        break

else:
    print("No pending videos found.")
