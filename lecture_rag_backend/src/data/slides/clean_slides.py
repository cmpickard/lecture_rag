"""
clean_slides.py

Cleans extracted lecture slide text files for use with embedding models.

Transformations:
  - Strips structural boilerplate (SLIDE N, ---, [SLIDE BODY], [PRESENTER NOTES], header lines)
  - Removes placeholder text ("no notes for this slide", "no text on this slide")
  - Removes PowerPoint layout artifacts (} used as visual groupers)
  - Merges slide body + presenter notes into a single text block per slide
  - Skips slides with no meaningful content after cleaning
  - Normalizes whitespace

Output: one cleaned .txt per input file, written to output_cleaned/
"""

import os
import re

INPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output_cleaned")

PLACEHOLDER_BODY = "(no text on this slide)"
PLACEHOLDER_NOTES = "(no notes for this slide)"


def parse_slides(lines):
    """
    Parse raw lines into a list of (slide_num, body_lines, notes_lines) tuples.
    """
    slides = []
    current_num = None
    body_lines = []
    notes_lines = []
    section = None  # 'body' or 'notes'

    for line in lines:
        stripped = line.strip()

        # New slide
        m = re.match(r"^SLIDE (\d+)$", stripped)
        if m:
            if current_num is not None:
                slides.append((current_num, body_lines, notes_lines))
            current_num = int(m.group(1))
            body_lines = []
            notes_lines = []
            section = None
            continue

        if stripped == "[SLIDE BODY]":
            section = "body"
            continue
        if stripped == "[PRESENTER NOTES]":
            section = "notes"
            continue

        # Skip structural/header lines
        if (
            stripped.startswith("====")
            or stripped == "-" * 40
            or stripped.startswith("PRESENTATION:")
            or stripped.startswith("FOLDER:")
            or stripped.startswith("TOTAL SLIDES:")
        ):
            continue

        if section == "body":
            body_lines.append(stripped)
        elif section == "notes":
            notes_lines.append(stripped)

    # Don't forget the last slide
    if current_num is not None:
        slides.append((current_num, body_lines, notes_lines))

    return slides


def clean_text(text):
    """Apply text-level cleaning to a string."""
    # Remove } grouping artifacts from PowerPoint layouts
    text = re.sub(r"\s*}\s*", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_slide_text(body_lines, notes_lines):
    """
    Combine body and notes lines into a single clean string.
    Returns None if there's no meaningful content.
    """
    body = " ".join(
        line for line in body_lines
        if line and line != PLACEHOLDER_BODY
    )
    notes = " ".join(
        line for line in notes_lines
        if line and line != PLACEHOLDER_NOTES
    )

    body = clean_text(body)
    notes = clean_text(notes)

    parts = [p for p in (body, notes) if p]
    if not parts:
        return None

    return " ".join(parts)


def get_presentation_name(lines):
    for line in lines[:6]:
        if line.startswith("PRESENTATION:"):
            return line.replace("PRESENTATION:", "").strip()
    return ""


def clean_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Strip newlines for parsing
    lines = [l.rstrip("\n") for l in lines]

    presentation_name = get_presentation_name(lines)
    slides = parse_slides(lines)

    output_blocks = []
    if presentation_name:
        output_blocks.append(f"# {presentation_name}")

    skipped = 0
    kept = 0
    for slide_num, body_lines, notes_lines in slides:
        text = build_slide_text(body_lines, notes_lines)
        if text is None:
            skipped += 1
            continue
        output_blocks.append(f"[Slide {slide_num}] {text}")
        kept += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(output_blocks))
        f.write("\n")

    return kept, skipped


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_files = sorted(
        f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")
    )

    total_kept = 0
    total_skipped = 0

    for filename in input_files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        kept, skipped = clean_file(input_path, output_path)
        total_kept += kept
        total_skipped += skipped
        print(f"{filename}: {kept} slides kept, {skipped} skipped (no content)")

    print(f"\nDone. {len(input_files)} files processed.")
    print(f"Total slides kept: {total_kept}, skipped: {total_skipped}")


if __name__ == "__main__":
    main()
