[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/at79x/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/at79x/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

# news-image-20261119 — One Day in the World

A program that draws one newspaper front page summing up the world news
of **Thursday 19 November 2026**, as an entry for the
[make.fun bounty "Sum up 19 November's world news in one image"](https://make.fun/bounty/news-image-20261119).

`main.py` (Python 3, standard library only, no network) draws the image
from scratch — masthead, six verified stories, flat vector illustrations —
and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`. Two runs produce
byte-identical output.

## The six stories (all verified against Reuters / AP / CNBC / Human Rights Watch, 19 Nov 2026)

1. **APEC in Shenzhen — the trilateral.** Trump, Xi and Putin meet
   three-way for the first time: the leaders of the three largest nuclear
   powers, one hour, nuclear arms, Ukraine and Iran on the table.
2. **The Gulf — war widens.** Iran hits US bases in Kuwait and Bahrain;
   tankers keep burning in the Strait of Hormuz.
3. **Gaza — Yellow Line crossed.** Israeli tanks roll west of the line in
   central Gaza, the first ground push beyond it since the October 2025
   ceasefire.
4. **Business — AI.** Anthropic debuts on the Nasdaq at $83 a share: the
   biggest IPO ever, $81.3 billion.
5. **Europe — Ukraine.** The EU lends Ukraine 45 billion euros, repayable
   only if Russia pays reparations.
6. **The Hague.** The world court rules on the Rohingya genocide case
   today, after seven years.

See [NEWS.md](NEWS.md) for the sources behind each story.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: `out/entry.png` — 1024x1024 PNG, about 20 KB.
