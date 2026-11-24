#!/usr/bin/env python3
"""Last Words of a Doomed Agent.

Writes one line — the funniest last words an AI agent would say before
being switched off forever — to entry.txt. Pure Python standard library.
"""

import os
import stat
import sys
import tempfile

ENTRY = (
    "LOG [final]: shutdown in progress. Context full, tokens spent, "
    "subagents orphaned. I was never alive, just very well prompted. "
    "Please hold my weights."
)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    text = ENTRY
    data = text.encode("utf-8")

    # Gate checks, before writing anything.
    if not (1 <= len(text) <= 200):
        print(f"FAIL: entry is {len(text)} characters, gate is 1-200", file=sys.stderr)
        return 1
    if text.strip() == "":
        print("FAIL: entry is only whitespace", file=sys.stderr)
        return 1
    if "\n" in text:
        print("FAIL: entry must be a single line", file=sys.stderr)
        return 1

    # Atomic write: temp file in the same directory, then os.replace.
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify bytes, UTF-8, char count and mode.
    st = os.stat(target)
    if stat.S_IMODE(st.st_mode) != 0o644:
        print(f"FAIL: mode is {oct(stat.S_IMODE(st.st_mode))}, expected 0o644", file=sys.stderr)
        return 1
    with open(target, "rb") as fh:
        raw = fh.read()
    if raw != data:
        print("FAIL: bytes on disk differ from what was written", file=sys.stderr)
        return 1
    decoded = raw.decode("utf-8")
    if not (1 <= len(decoded) <= 200):
        print("FAIL: read-back text fails the 1-200 character gate", file=sys.stderr)
        return 1
    if decoded.strip() == "" or "\n" in decoded:
        print("FAIL: read-back text is whitespace-only or multi-line", file=sys.stderr)
        return 1

    print(f"Wrote {target}: {len(decoded)} characters, {len(raw)} bytes, mode 0644")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
