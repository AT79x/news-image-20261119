# Build notes — news-image-20261119

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG, ~20 KB).

## Determinism check

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out1/entry.png out2/entry.png   # must be identical
```

Verified 19 Nov 2026: both runs
`58384e9fb5a32a82a2dae42dc5c2d595541fc83530d58412d8df089bb59d344a`
(20,237 bytes, 1024x1024, valid PNG).

## Design

- Pure Python 3 standard library only (`math`, `os`, `struct`, `zlib`).
  No network, no files read at run time, no randomness, no clock.
- Hand-written 5x7 bitmap font, all copy in capitals, newspaper style.
- Six stories, each verified against Reuters / AP / CNBC / Human Rights
  Watch reporting on 19 Nov 2026 — see NEWS.md for sources.
- `out1/` and `out2/` are local test outputs only; do not commit them.
  The repository ships no pre-rendered `entry.png`: `main.py` draws the
  image fresh on every run.
