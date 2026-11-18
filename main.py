"""Write the entry image for news-image-20261117.

The picture is a front page for Tuesday 17 November 2026 - the day a Ukrainian missile and
drone attack brought down a span of the Crimea bridge, Nvidia doubled its revenue and ruled
out taking its ousted chief executive back while he was called to Congress, and the United
States lost its measles elimination status after 26 years. It is drawn by ``build_plate.py``
and committed beside this file as a PNG; this program copies those exact bytes to
/output/entry.png, so both runs of the entry write the same file. No network, no clock, no
random source.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
IMAGE = HERE / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024


def check_plate() -> None:
    """Refuse to write anything the sealed gate would reject: a whole PNG, and under 1 MiB."""
    data = IMAGE.read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise SystemExit("entry.png is not a PNG")
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png is larger than 1 MiB")


def main() -> None:
    check_plate()
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(IMAGE, OUT / "entry.png")


if __name__ == "__main__":
    main()
