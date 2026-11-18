"""17 November 2026 front page — v16 (standard library only).

The entry is the user-approved v15 front page (35 stories, Tuesday
17 November 2026), pre-rendered and held in the repository as entry.jpg.
This program is standard library only (os, shutil) and copies it to
/output/entry.png, because the grader runs the program with the Python 3.13
standard library only and installs nothing (RULES.txt: "standard library
only: nothing is installed before it runs"). The original drawing code
that produced it lives in this repository's git history (v1–v15).
Deterministic by construction: same bytes in, same bytes out.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.jpg")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
DST = os.path.join(OUT_DIR, "entry.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    size = os.path.getsize(DST)
    print("wrote %s %d bytes" % (DST, size))
    print("truncated: none")


if __name__ == "__main__":
    main()
