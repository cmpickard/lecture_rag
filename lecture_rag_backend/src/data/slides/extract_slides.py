"""
extract_slides.py
-----------------
Finds all Google Slides presentations inside a root Drive folder (recursively,
including all subfolders), extracts the slide body text and presenter notes from
each one, and saves each presentation as a plain text file ready for chunking
and embedding.

The folder path (e.g. "RAG Slides > PHIL101") is recorded in each output file
as metadata, so you know which course each chunk came from.

BEFORE RUNNING:
  1. Follow SETUP_GUIDE.md to get your credentials.json file
  2. Install dependencies:
       pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
  3. Set ROOT_FOLDER_NAME below to the name of your top-level folder
  4. Run this script:
       python extract_slides.py

OUTPUT:
  A folder called "output/" will be created containing one .txt file per
  presentation, named after the presentation title.
"""

import os
import re
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Configuration ─────────────────────────────────────────────────────────────

# The name of your top-level Google Drive folder.
# The script will search this folder and ALL subfolders within it recursively.
# This should be unique in your Drive to avoid ambiguity (see SETUP_GUIDE.md).
ROOT_FOLDER_NAME = "RAG Slides"

# Where to save the output text files
OUTPUT_DIR = "output"

# ── Auth setup (you don't need to change anything below this line) ─────────────

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/presentations.readonly",
]


def authenticate():
    """
    Handles Google OAuth login.
    On first run, opens a browser for you to approve access.
    Saves a token.json file so you don't have to log in again.
    """
    creds = None

    # Reuse saved credentials if they exist
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, prompt login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "credentials.json not found! "
                    "Please follow SETUP_GUIDE.md to download your credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return creds


# ── Drive: finding your files ──────────────────────────────────────────────────

FOLDER_MIME = "application/vnd.google-apps.folder"
SLIDES_MIME = "application/vnd.google-apps.presentation"


def find_root_folder(drive_service, folder_name):
    """
    Looks up a folder by name in Google Drive and returns its ID.
    Raises an error if the name matches zero or more than one folder,
    since either case means we can't be sure we have the right one.
    """
    query = (
        f"name = '{folder_name}' "
        f"and mimeType = '{FOLDER_MIME}' "
        f"and trashed = false"
    )
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if not folders:
        raise FileNotFoundError(
            f"No folder named '{folder_name}' found in your Drive. "
            f"Check the spelling and make sure it hasn't been trashed."
        )
    if len(folders) > 1:
        ids = ", ".join(f["id"] for f in folders)
        raise ValueError(
            f"Found {len(folders)} folders named '{folder_name}' in your Drive. "
            f"Please rename them so the root folder is unique. IDs found: {ids}"
        )

    folder_id = folders[0]["id"]
    print(f"  ✓ Found root folder: '{folder_name}' (id: {folder_id})")
    return folder_id


def list_children(drive_service, parent_id, mime_type):
    """
    Returns all items of a given MIME type that are direct children
    of parent_id. Handles pagination automatically.
    """
    items = []
    query = (
        f"mimeType = '{mime_type}' "
        f"and '{parent_id}' in parents "
        f"and trashed = false"
    )
    page_token = None
    while True:
        results = drive_service.files().list(
            q=query,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
            pageSize=100,
        ).execute()
        items.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    return items


def collect_slides_recursively(drive_service, folder_id, folder_path):
    """
    Walks a folder tree depth-first starting at folder_id.
    Returns a list of dicts, one per Slides file found, each containing:
      - id:          the file's Drive ID
      - name:        the file's title
      - folder_path: the human-readable path to its containing folder
                     (e.g. "RAG Slides > PHIL101")
    """
    found = []

    # Collect any Slides files directly in this folder
    slides_files = list_children(drive_service, folder_id, SLIDES_MIME)
    for f in slides_files:
        found.append({
            "id": f["id"],
            "name": f["name"],
            "folder_path": folder_path,
        })

    # Recurse into each subfolder
    subfolders = list_children(drive_service, folder_id, FOLDER_MIME)
    for subfolder in subfolders:
        child_path = f"{folder_path} > {subfolder['name']}"
        print(f"  → Scanning: {child_path}")
        found.extend(
            collect_slides_recursively(drive_service, subfolder["id"], child_path)
        )

    return found


# ── Slides: extracting text ────────────────────────────────────────────────────

def extract_text_from_elements(page_elements):
    """
    Walks through a list of page elements (shapes, tables, etc.)
    and collects all text content into a single string.
    """
    texts = []
    for element in page_elements:
        shape = element.get("shape", {})
        text_content = shape.get("text", {})
        for text_element in text_content.get("textElements", []):
            text_run = text_element.get("textRun", {})
            content = text_run.get("content", "").strip()
            if content:
                texts.append(content)

        # Also handle tables (each cell is its own text block)
        table = element.get("table", {})
        for row in table.get("tableRows", []):
            for cell in row.get("tableCells", []):
                for text_element in cell.get("text", {}).get("textElements", []):
                    text_run = text_element.get("textRun", {})
                    content = text_run.get("content", "").strip()
                    if content:
                        texts.append(content)

    return " ".join(texts)


def extract_notes_text(notes_page):
    """
    Extracts the presenter notes text from a slide's notes page.
    The notes text box has shapeType BODY or TEXT_BOX — we grab all text
    from all shapes except the slide thumbnail placeholder.
    """
    notes_texts = []
    for element in notes_page.get("pageElements", []):
        shape = element.get("shape", {})
        # Skip the slide image placeholder (shapeType RECTANGLE or similar)
        placeholder = shape.get("placeholder", {})
        if placeholder.get("type") == "SLIDE_IMAGE":
            continue
        for text_element in shape.get("text", {}).get("textElements", []):
            text_run = text_element.get("textRun", {})
            content = text_run.get("content", "").strip()
            if content:
                notes_texts.append(content)
    return " ".join(notes_texts)


def extract_presentation(slides_service, presentation_id, presentation_title, folder_path):
    """
    Fetches a full presentation and returns its content as a formatted string,
    with each slide's body text and notes clearly separated.
    folder_path is recorded in the file header as metadata.
    """
    print(f"  Fetching slides...")
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    slides = presentation.get("slides", [])
    output_lines = []
    output_lines.append(f"PRESENTATION: {presentation_title}")
    output_lines.append(f"FOLDER:       {folder_path}")
    output_lines.append(f"TOTAL SLIDES: {len(slides)}")
    output_lines.append("=" * 60)
    output_lines.append("")

    for i, slide in enumerate(slides, start=1):
        slide_number = f"SLIDE {i}"
        output_lines.append(slide_number)
        output_lines.append("-" * 40)

        # --- Body text ---
        page_elements = slide.get("pageElements", [])
        body_text = extract_text_from_elements(page_elements)
        if body_text:
            output_lines.append("[SLIDE BODY]")
            output_lines.append(body_text)
        else:
            output_lines.append("[SLIDE BODY]")
            output_lines.append("(no text on this slide)")

        output_lines.append("")

        # --- Presenter notes ---
        notes_page = slide.get("slideProperties", {}).get("notesPage", {})
        if notes_page:
            notes_elements = notes_page.get("pageElements", [])
            notes_text = extract_notes_text(notes_page)
            if notes_text:
                output_lines.append("[PRESENTER NOTES]")
                output_lines.append(notes_text)
            else:
                output_lines.append("[PRESENTER NOTES]")
                output_lines.append("(no notes for this slide)")
        else:
            output_lines.append("[PRESENTER NOTES]")
            output_lines.append("(no notes for this slide)")

        output_lines.append("")
        output_lines.append("")  # Extra blank line between slides

    return "\n".join(output_lines)


# ── File saving ────────────────────────────────────────────────────────────────

def safe_filename(title):
    """
    Converts a presentation title into a safe filename by removing
    characters that aren't allowed in filenames.
    Example: "CS101: Week 4 / Sorting" → "CS101_Week_4_Sorting.txt"
    """
    safe = re.sub(r'[\\/*?:"<>|]', "", title)   # Remove forbidden chars
    safe = re.sub(r'\s+', "_", safe.strip())      # Replace spaces with underscores
    return safe + ".txt"


def save_text(output_dir, filename, content):
    """Saves a string to a .txt file in the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n🔐 Authenticating with Google...")
    creds = authenticate()
    drive_service = build("drive", "v3", credentials=creds)
    slides_service = build("slides", "v1", credentials=creds)
    print("✓ Authenticated successfully.\n")

    # Find the root folder by name (must be unique in your Drive)
    print(f"🔍 Looking for root folder: '{ROOT_FOLDER_NAME}'...")
    root_id = find_root_folder(drive_service, ROOT_FOLDER_NAME)
    print()

    # Walk the full folder tree from the root
    print(f"📂 Scanning folder tree under '{ROOT_FOLDER_NAME}'...")
    slides_files = collect_slides_recursively(drive_service, root_id, ROOT_FOLDER_NAME)
    print()

    if not slides_files:
        print("No Google Slides files found under that folder. Check the folder contents and try again.")
        return

    print(f"✓ Found {len(slides_files)} presentation(s).\n")

    # Process each presentation
    success_count = 0
    fail_count = 0

    for idx, file_info in enumerate(slides_files, start=1):
        file_id = file_info["id"]
        file_name = file_info["name"]
        folder_path = file_info["folder_path"]
        print(f"[{idx}/{len(slides_files)}] Processing: {file_name}")
        print(f"  Location: {folder_path}")

        try:
            content = extract_presentation(slides_service, file_id, file_name, folder_path)
            filename = safe_filename(file_name)
            filepath = save_text(OUTPUT_DIR, filename, content)
            print(f"  ✓ Saved to: {filepath}\n")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Error processing '{file_name}': {e}\n")
            fail_count += 1

    # Summary
    print("=" * 60)
    print(f"Done! {success_count} file(s) extracted successfully.")
    if fail_count:
        print(f"      {fail_count} file(s) failed (see errors above).")
    print(f"Output folder: {os.path.abspath(OUTPUT_DIR)}/")


if __name__ == "__main__":
    main()
