# Google API Setup Guide
## For: Lecture Notes Extraction Script

This guide walks you through getting Google API credentials so the extraction
script can read your Google Slides files. You only need to do this once.

---

## Step 1: Create a Google Cloud Project

1. Go to https://console.cloud.google.com
2. Sign in with the Google account that owns your Slides files
3. Click the project dropdown at the top of the page (it might say "Select a project")
4. Click **"New Project"**
5. Give it any name (e.g. "Lecture Notes Extractor") and click **Create**
6. Make sure your new project is selected in the dropdown before continuing

---

## Step 2: Enable the Required APIs

You need to turn on two APIs: Google Drive and Google Slides.

1. In the left sidebar, go to **APIs & Services > Library**
2. Search for **"Google Drive API"**, click it, then click **Enable**
3. Go back to the Library, search for **"Google Slides API"**, click it, then click **Enable**

---

## Step 3: Create OAuth Credentials

This lets the script log in as you (so it can see your private files).

1. Go to **APIs & Services > Credentials**
2. Click **"+ Create Credentials"** at the top, then choose **"OAuth client ID"**
3. If prompted to configure the consent screen first:
   - Click **"Configure Consent Screen"**
   - Choose **"External"** and click Create
   - Fill in just the required fields: App name (anything), User support email (your email),
     Developer contact email (your email)
   - Click **Save and Continue** through all the steps — you don't need to add scopes manually
   - On the last page click **Back to Dashboard**
   - Then go back to **Credentials > + Create Credentials > OAuth client ID**
4. For **Application type**, choose **"Desktop app"**
5. Give it a name (anything, e.g. "Extractor") and click **Create**
6. A popup will show your client ID and secret — click **"Download JSON"**
7. Save the downloaded file as `credentials.json` in the same folder as the script

---

## Step 4: Set Up Python

If you don't have Python installed, download it from https://www.python.org/downloads/
(get Python 3.8 or newer). Make sure to check "Add Python to PATH" during install.

Then open a terminal (Mac: Terminal app; Windows: Command Prompt or PowerShell)
and install the required libraries by running:

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Step 5: First Run (Authorization)

The first time you run the script, a browser window will open asking you to
log in to Google and grant the app permission to read your Drive and Slides.

- You may see a warning that says "Google hasn't verified this app" — this is
  normal for personal scripts. Click **"Advanced"** then **"Go to [App Name] (unsafe)"**
- Click through to grant access

After you approve, a file called `token.json` will be saved automatically.
The script will use this file for all future runs — you won't need to log in again.

---

## Folder Structure When You're Ready

Your working folder should look like this:

```
lecture_extractor/
├── credentials.json       ← downloaded from Google Cloud Console
├── extract_slides.py      ← the extraction script
└── output/                ← folder will be created automatically
```

The `token.json` file will appear here after your first run.
