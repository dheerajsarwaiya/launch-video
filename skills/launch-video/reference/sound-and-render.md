# Sound, review sheets, render

Every Python script runs through `uv run --with numpy --with imageio-ffmpeg python3 …` — imageio-ffmpeg ships a full ffmpeg, so nothing installs system-wide. Get that ffmpeg once:

```bash
F=$(uv run --quiet --with imageio-ffmpeg python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")
```

## Sound

**Plan in beats, whatever the music.** Pick or measure a tempo; every scene boundary lands on a beat and every cue is `bar, beat` on that grid, never a literal frame. Silent film → plan at 120 BPM anyway.

**"I compose it" (synthesised).** Write music and effects as one piece: effects in the same key and the same space as the music, blended in rather than laid on top. Mix it like a real track — effects sit softly under the music, nothing harsh or spiky, repeated little sounds stay in the background. The tempo is yours, so the grid is known.

**"Your own track."** The user supplies it and owns the rights; store it in `work/music/` and note its source.
1. Measure the grid: `scripts/beats.py --drums song.mp3 --out work/beats.json` (stems as `--stem name=file` if available; `--bpm` if known). `gridCheckMs.spread` under 10 ms is good.
2. Print each bar's loudness from `beats.json` and read the song's shape: sparse intro, where drums enter, the drop, the outro. Put the hook on the first strong bar (cut slow intros), the strongest moment on the drop, the ending on the ring-out.
3. Cut the song on bars to the film's length with ffmpeg (`atrim` per segment, 5 ms fades at each join, a fade-out at the end). Film length = a whole number of bars.

**Effects** (either path): short, dry, quiet (volume 0.25–0.5); one per meaningful event — a tap, a stamp landing, the reveal. Place each so its peak, not its start, lands on the cue.

## Review sheets

Stills: capture the chosen frames from the same page the render uses. Stack four into one sheet to save tokens:

```bash
$F -v error -y -i a.png -i b.png -i c.png -i d.png -filter_complex \
  "[0:v]scale=960:-1[a];[1:v]scale=960:-1[b];[2:v]scale=960:-1[c];[3:v]scale=960:-1[d];[a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0" sheet.png
```

Contact sheet of a half-size draft (one tile every 0.4 s at 30 fps):

```bash
$F -v error -y -i work/draft.mp4 -vf "select='not(mod(n\,12))',scale=240:-1,tile=8x8:padding=4:color=0x333333" -frames:v 1 -vsync vfr work/contact.png
```

## Render

- 30 fps (60 only for a lot of fast motion). 1920×1080, 1080×1920 or 1080×1080.
- Encode: `-c:v libx264 -crf 18 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart`, audio `-c:a aac -b:a 256k`.
- Frames captured as full-range RGB PNG and encoded with the flags above stay true. If the background decodes lighter than its token (`#0a0a0a` → `#171717`), the color range was read wrong: fix the encode, never the tokens.
- Poster: extract the settled frame to `poster.jpg`, then overwrite frame 0 with it (re-encode with the poster as the first image of the sequence) so every platform's thumbnail shows it.
- Muted loop (landing page only): same encode, `-an`, and the last frame equals the first.

## Verify

```bash
uv run --with numpy --with imageio-ffmpeg python3 scripts/verify.py launch-video/vN/launch.mp4 \
  --duration <s> --poster launch-video/vN/poster.jpg [--bg r,g,b] [--loop] [--silent]
```

It checks duration to the frame, that audio exists, that frame 0 is the poster, the background's decoded color, and the loop seam. Report its output to the user.
