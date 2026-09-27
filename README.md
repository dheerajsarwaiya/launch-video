# launch-video

An agent skill that turns a project directory or a website URL into a short launch video (15–60 s) with music, motion and share copy.

It works in stages and stops twice for your OK:

1. **Discover**: reads the code or the live site for the real UI, colors, fonts and claims.
2. **Interview**: asks four questions (where it plays, what it shows, tone, music).
3. **Script** (gate 1): a scene table checked by `scripts/script-check.py` for timing, reading time and a source for every claim.
4. **Style frames** (gate 2): three full-size stills to approve before the full build.
5. **Build**: an HTML page per scene driven by one clock, captured headless, encoded with ffmpeg.
6. **Review**: stills and a contact sheet, checked against a fixed list.
7. **Render and verify**: `scripts/verify.py` decodes the final file and checks duration, audio, the poster frame and color range.

Output goes to `launch-video/v1/`, `v2/` and so on: `launch.mp4`, `poster.jpg`, `share-copy.txt`.

## Install

```bash
npx skills add dheerajsarwaiya/launch-video
```

Or copy `skills/launch-video/` into `~/.claude/skills/`.

Then ask your agent to "make a launch video", or pass it a URL.

## Requirements

- [`uv`](https://docs.astral.sh/uv/). The scripts run with `uv run --with numpy --with imageio-ffmpeg`, which brings its own ffmpeg, so nothing is installed system-wide.
- A headless browser (Playwright, Puppeteer or Chrome) for capturing frames.

## Credits

Derived from [`brag-slim`](https://github.com/latent-spaces/brag) by Shunit Haviv Hakimi (MIT). `scripts/beats.py` and `scripts/verify.py` come from [product-film](https://github.com/Rieranthony/product-film-skill) by Rieranthony (MIT).

## License

MIT
