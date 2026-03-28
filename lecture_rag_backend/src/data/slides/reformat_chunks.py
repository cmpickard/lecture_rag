"""
reformat_chunks.py

Reformats chunks.jsonl to match the Postgres schema:
  course_title, lecture_title, slide_start, slide_end, content

Transformations:
  - course "PHIL_1000"                        -> course_title "PHIL 1000"
  - lecture_title "PHIL 1000 - 00 - Intro"   -> lecture_title "Intro"
  - text                                      -> content
  - lecture_id                                -> dropped
"""

import json
import re

INPUT = "chunks.jsonl"
OUTPUT = "chunks_reformatted.jsonl"


def course_title(raw):
    """"PHIL_1000" -> "PHIL 1000" """
    return raw.replace("_", " ")


def lecture_title(raw):
    """
    Strip the course + optional lecture-number prefix from the title.
    "PHIL 1000 - 00 - Course Intro"  -> "Course Intro"
    "PHIL 1000 - The Problem of Evil" -> "The Problem of Evil"
    """
    return re.sub(r"^[A-Z]+ \d+ - (?:\d+ - )?", "", raw)


def reformat(chunk):
    return {
        "course_title":   course_title(chunk["course"]),
        "lecture_title":  lecture_title(chunk["lecture_title"]),
        "slide_start":    chunk["slide_start"],
        "slide_end":      chunk["slide_end"],
        "content":        chunk["text"],
    }


with open(INPUT, encoding="utf-8") as fin, \
     open(OUTPUT, "w", encoding="utf-8") as fout:
    for line in fin:
        chunk = json.loads(line)
        fout.write(json.dumps(reformat(chunk), ensure_ascii=False) + "\n")

print(f"Done. Written to {OUTPUT}")
