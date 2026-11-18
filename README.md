# The world in one picture — 17 November 2026

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/edoyacen/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/edoyacen/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

One image that sums up Tuesday 17 November 2026, for [make.fun's](https://make.fun)
`news-image-20261117` bounty ([bounty page](https://make.fun/bounty/news-image-20261117)).

The day turned on two places far apart and one war in between. Xi Jinping opened APEC in
Shenzhen with a message about Chinese power, and in Manila hundreds were arrested in protests
against the Iran war and an AI pact signed with Washington. The plate draws the South China
Sea between them, because the distance is the story.

Beneath that lead: five EU states announced plans to send migrants to "return hubs" in Rwanda;
Jensen Huang was called to testify before Congress over a possible national security breach;
the Knesset elected a speaker backed by Benjamin Netanyahu's opponents; and Brazil recorded
1,605 pesticide poisoning reports in a year, in the same week an isolated tribe emerged from
the Amazon.

## How it is made

`plate.html` is the whole picture: one SVG plate, 1024 by 1024, set in Georgia and Arial, so
it renders identically anywhere and holds no external asset. `entry.png` is that plate
rendered. `main.py` copies the image to `/output/entry.png` byte for byte, touching no
network, no clock and no random source, so two runs write the same file.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Files

| File | What it is |
| --- | --- |
| `entry.png` | the entry image, 1024x1024 |
| `plate.html` | the source plate it is rendered from |
| `main.py` | writes the image to the output directory, deterministically |
| `LICENSE` | MIT |
