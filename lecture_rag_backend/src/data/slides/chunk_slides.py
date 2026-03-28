"""
chunk_slides.py

Chunks cleaned lecture slide files for use with embedding models.

Strategy: sliding window over slides (default: window=4, stride=2).
Each chunk is a JSON object with text + metadata, written as JSON Lines
to chunks.jsonl.

Usage:
    python chunk_slides.py                      # default window=4, stride=2
    python chunk_slides.py --window 3 --stride 1
"""

import os
import re
import json
import argparse

INPUT_DIR = os.path.join(os.path.dirname(__file__), "output_cleaned")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "chunks.jsonl")


def parse_cleaned_file(path):
    """
    Parse a cleaned file into (lecture_title, slides).

    Returns:
        lecture_title: str
        slides: list of (slide_num: int, text: str)
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")

    lecture_title = ""
    slides = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            lecture_title = block[2:].strip()
        else:
            m = re.match(r"^\[Slide (\d+)\]\s+(.*)", block, re.DOTALL)
            if m:
                slides.append((int(m.group(1)), m.group(2).strip()))

    return lecture_title, slides


def extract_course(filename):
    """
    Extract course code from filename.
    e.g. "PHIL_1000_-_01_-_Intro_to_Arguments.txt" -> "PHIL_1000"
    """
    m = re.match(r"^([A-Z]+_\d+)", filename)
    return m.group(1) if m else "UNKNOWN"


def make_chunks(lecture_title, slides, lecture_id, course, window_size, stride):
    """
    Produce sliding-window chunks from a list of slides.

    Each chunk contains `window_size` consecutive slides (or fewer at the end)
    and advances by `stride` slides each step.
    """
    chunks = []
    n = len(slides)

    for start in range(0, n, stride):
        window = slides[start : start + window_size]
        slide_nums = [s[0] for s in window]
        chunk_text = "\n\n".join(f"[Slide {num}] {text}" for num, text in window)

        chunks.append({
            "course": course,
            "lecture_id": lecture_id,
            "lecture_title": lecture_title,
            "slide_start": slide_nums[0],
            "slide_end": slide_nums[-1],
            "text": chunk_text,
        })

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Chunk cleaned lecture slides for RAG.")
    parser.add_argument("--window", type=int, default=4, help="Number of slides per chunk (default: 4)")
    parser.add_argument("--stride", type=int, default=2, help="Slide advance between chunks (default: 2)")
    parser.add_argument("--input_dir", default=INPUT_DIR, help="Directory of cleaned .txt files")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output .jsonl file path")
    args = parser.parse_args()

    input_files = sorted(f for f in os.listdir(args.input_dir) if f.endswith(".txt"))

    total_chunks = 0
    total_files = 0

    with open(args.output, "w", encoding="utf-8") as out:
        for filename in input_files:
            path = os.path.join(args.input_dir, filename)
            lecture_id = filename.removesuffix(".txt")
            course = extract_course(filename)

            lecture_title, slides = parse_cleaned_file(path)

            if not slides:
                print(f"WARNING: no slides found in {filename}, skipping.")
                continue

            chunks = make_chunks(
                lecture_title=lecture_title,
                slides=slides,
                lecture_id=lecture_id,
                course=course,
                window_size=args.window,
                stride=args.stride,
            )

            for chunk in chunks:
                out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

            total_chunks += len(chunks)
            total_files += 1
            print(f"{filename}: {len(slides)} slides -> {len(chunks)} chunks")

    print(f"\nDone. {total_files} files, {total_chunks} total chunks -> {args.output}")


if __name__ == "__main__":
    main()
