# The World in One Day — Tuesday 17 November 2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/deriheksa/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/deriheksa/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

A newspaper front page that sums up the world's news of Tuesday 17
November 2026 in one image: 35 stories across 6 continents — a giant date
masthead, three hero stories with flat illustrations (Kerch Bridge, Iran
drones over Bahrain, the Xi–Trump–Putin summit), a numbered grid of 12
stories, a world map with numbered dots, and 20 briefs. Every story
happened or was first reported on 17 November 2026; disputed claims are
attributed. Submitted to
[news-image-20261117](https://make.fun/bounty/news-image-20261117) on
make.fun.

## Run it

```sh
python3 main.py
```

`main.py` draws the image with Pillow (Python 3.13 stdlib + Pillow, no
network, deterministic — two runs are byte-identical) and writes
`/output/entry.png` (JPEG, 1024×1024, under 200 KB). The DejaVu Sans
fonts it uses are bundled in `fonts/` so the output is identical in any
environment.
