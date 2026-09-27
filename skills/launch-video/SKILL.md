---
name: launch-video
description: Make a short launch video (15–60 s) with music, motion and share copy from a project directory or a website URL — interviews the user, gets the script approved, then builds, checks and renders. Use for "make a launch video", "promo video", "product film", "brag about this", or showing off what was built.
---

# Launch video

A modern, slick launch video that looks like the product made it: its real UI, colors, type and voice. The user decides what goes in; you decide how it's made. Two **gates** stop the run for the user's OK — the script, then the style frames. Nothing past a gate is built before the user answers it.

Deliverables go to `launch-video/` in the current directory, one folder per version: `v1/`, `v2/`, … (never overwrite a version). Intermediates (frames, downloads, stems, scripts) go in `launch-video/work/`.

## 1. Discover

Decide the input, then collect just enough to name real options in the interview.

| Input | Recognise it | Material comes from |
|---|---|---|
| Project | No input, and the current directory is a project | The code |
| Website | An `http(s)://` URL or a bare domain | The live site |

Neither → ask what to make a video about.

- **Project:** the main page, global CSS (exact color tokens, fonts and where they load), README, routes, the key components. Find the product **in use**: entry → key action → result.
- **Website:** fetch it; if the HTML is an empty JS shell, load it in a headless browser, dismiss overlays, scroll section by section. Take headline, tagline, feature names, CTAs, meta and social tags, colors from the CSS, loaded fonts, logo, screenshots and demo videos (download the ones you'll use).
- **Claims and voice — both inputs.** Read `CLAUDE.md`, `AGENTS.md`, `docs/brand*`, positioning docs, and any memory notes. Write down: what the product does, what it deliberately does **not** do (removed features are the easiest wrong thing to show), who it speaks to, approved lines, banned words.

If `launch-video/BRAND.md` already exists from an earlier run, read it first and ask only what it leaves open.

Done when you can list the 3–6 strongest features by their product names, and the claims list is written.

## 2. Interview

One AskUserQuestion call, 4 questions, every option drawn from what discovery found. Put your recommendation first, marked "(Recommended)".

| Question | Options |
|---|---|
| Where will it play? | Social with sound, 16:9 / Social vertical, 9:16 / Landing page, muted loop / Launch or demo page |
| What must it show? (multiSelect) | The strongest features, by their real names |
| What tone? | 3 of the presets in [reference/craft.md](reference/craft.md) that fit this product, best fit first |
| Music? | I compose it (synthesised, no licence needed) / Your own track (you have the rights) / Silent |

Ask a second round only for what is still open: length if not 15–25 s, the ending (tagline, URL, CTA), a feature to focus on, dark vs light. Never ask what the code answers (colors, fonts, spacing).

Write the answers and the claims list into `launch-video/BRAND.md`: brief, colors (hex), fonts, voice rules, claims (does / never does / approved lines), each with its source. It outlives this run.

## 3. Script — gate 1

Read [reference/craft.md](reference/craft.md) first. Write `launch-video/script.md`:

1. **Angle** — one sentence: what it is, who it's for, why it's different.
2. **Hook** — what happens in the first 2 seconds.
3. **The table**, exactly this header:

   ```
   | # | Scene | Secs | Read | Words | Source |
   ```

   `Secs` = scene length. `Read` = seconds the words sit fully on screen and settled. `Words` = the on-screen text verbatim, `-` for none. `Source` = where each claim comes from (file, URL, or `user`).
4. Under the table, one line per scene: **what moves** (the real UI doing what, beat by beat).
5. **Share caption** — 1–3 sentences, postable as is.

Run `python3 scripts/script-check.py launch-video/script.md --duration <target>` and fix until it prints `script ok`. Then read every Words cell against the claims list in BRAND.md — the checker proves a source exists, you prove it says what the line claims.

**Stop.** Show the user the script (angle, hook, table, what-moves lines, caption) and wait. Fold every note into script.md and BRAND.md, re-run the checker, show again if the change was more than wording.

## 4. Style frames — gate 2

Build only enough to render 3 stills at full size: the hook, the strongest feature scene, the ending. Look at each yourself first (overflow, collisions, contrast, text readable at delivery size), then **stop** and show them. People answer pictures faster than questions; expect notes on shades, sizes and words, and write them into BRAND.md.

## 5. Build

Use what's on the machine. Default: an HTML page per scene driven by one clock, captured by a headless browser, encoded with ffmpeg. Use Remotion only if the project already has it.

- **Every frame is a pure function of time.** No CSS transitions or keyframes, timers, `Date.now()` or state carried between frames. A component that runs its own clock (spinner, motion library, video, async image) gets a frame-driven copy.
- Wait for fonts and images before capturing each frame.
- **Reuse the real thing**: the project's components, stylesheets, fonts, images; the site's markup and assets. Rebuild only what can't be reused, with the product's exact tokens.
- Keep a `data-target` on anything a cursor clicks or an element travels to, and print its measured box into a debug frame rather than guessing positions.

Sound: follow [reference/sound-and-render.md](reference/sound-and-render.md).

## 6. Review

Render stills from every scene **and** from the middle of every transition, then a contact sheet of the whole draft (commands in the sound-and-render reference). Check against the review list in [reference/craft.md](reference/craft.md). Fix and repeat until one full pass finds nothing. Show the user the contact sheet with a one-line note of what changed since the style frames.

## 7. Render, verify, deliver

Render to `launch-video/vN/` following [reference/sound-and-render.md](reference/sound-and-render.md), then run `scripts/verify.py` on the final file. Deliver only when it exits 0.

- `launch.mp4` — poster baked in as frame 0 (replace frame 0, never add one, so duration and sync hold).
- `poster.jpg` — the strongest **settled** frame (text fully in, not mid-transition).
- `share-copy.txt` — the approved caption.
- A muted loop too, if it plays on a landing page.

Tell the user: where the files are, the angle in one sentence, what verify checked. Offer to re-roll a scene or try another tone as `v{N+1}`. Ask before committing, pushing or publishing anything.
