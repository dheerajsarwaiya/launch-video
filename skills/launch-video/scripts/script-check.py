"""Check a launch-video script table before anyone sees it.

    python3 scripts/script-check.py launch-video/script.md --duration 20
    python3 scripts/script-check.py --selftest

Reads the first markdown table whose header is:
    | # | Scene | Secs | Read | Words | Source |
Secs  = how long the scene runs.
Read  = how long its words sit fully on screen and settled.
Words = the on-screen text, exactly as it will appear ("" or - for none).
Source = where every claim in Words comes from (file path, URL, or "user").

Fails (exit 1) when:
- the scenes do not add up to --duration (within 0.5 s)
- the first scene is longer than 3 s (the hook must land fast)
- a line needs more reading time than it gets (0.3 s per word)
- Read is longer than the scene it sits in
- a scene has words but no source
"""

import argparse
import re
import sys

SECONDS_PER_WORD = 0.3
HOOK_MAX = 3.0
COLUMNS = ["#", "scene", "secs", "read", "words", "source"]


def parse(text):
    rows = []
    in_table = False
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.strip().startswith("|"):
            if in_table:
                break
            continue
        if [c.lower() for c in cells] == COLUMNS:
            in_table = True
            continue
        if in_table and not re.fullmatch(r"[-: ]+", "".join(cells)):
            rows.append(dict(zip(COLUMNS, cells)))
    return rows


def words_in(text):
    text = text.strip().strip('"')
    return 0 if text in ("", "-") else len(text.split())


def check(rows, duration):
    problems = []
    if not rows:
        return ["no script table found (header: | # | Scene | Secs | Read | Words | Source |)"]
    total = sum(float(r["secs"]) for r in rows)
    if abs(total - duration) > 0.5:
        problems.append(f"scenes add up to {total:g}s, target is {duration:g}s")
    if float(rows[0]["secs"]) > HOOK_MAX:
        problems.append(f"scene 1 (the hook) runs {rows[0]['secs']}s, keep it to {HOOK_MAX:g}s or less")
    for r in rows:
        n, secs, read = words_in(r["words"]), float(r["secs"]), float(r["read"] or 0)
        need = n * SECONDS_PER_WORD
        if read > secs:
            problems.append(f"scene {r['#']}: Read {read:g}s is longer than the scene ({secs:g}s)")
        if need > read + 1e-9:
            problems.append(f"scene {r['#']}: {n} words need {need:.1f}s settled, gets {read:g}s")
        if n and r["source"] in ("", "-"):
            problems.append(f"scene {r['#']}: words with no source")
    return problems


def selftest():
    good = """
| # | Scene | Secs | Read | Words | Source |
|---|---|---|---|---|---|
| 1 | Hook | 2.5 | 1.5 | "Ship. Share. Smile." | README.md |
| 2 | Tap | 4 | 0 | - | - |
| 3 | Outro | 3.5 | 2 | "example.com" | user |
"""
    assert check(parse(good), 10) == [], check(parse(good), 10)
    bad = good.replace("| 1.5 |", "| 0.5 |").replace("README.md", "-")
    found = check(parse(bad), 12)
    assert any("add up" in p for p in found)
    assert any("need 0.9s" in p for p in found)
    assert any("no source" in p for p in found)
    print("selftest ok")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script", nargs="?")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    with open(args.script) as f:
        problems = check(parse(f.read()), args.duration)
    for p in problems:
        print("FAIL", p)
    if problems:
        sys.exit(1)
    print("script ok")


if __name__ == "__main__":
    main()
