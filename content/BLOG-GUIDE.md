# BrandexVideo blog publishing guide

This file is the standing brief for every automated blog run. Follow it exactly.

## Who we are (facts you may state)
- BrandexVideo (www.brandexvideo.com) is a remote short-form video editing studio for overseas clients: USA, UK, UAE, Canada, Australia, Singapore, Saudi Arabia. Studio and editors are in Chennai, India; clients are never Indian.
- Plans: $799 / 10 videos, $1,499 / 20 videos, $2,799 / 40 videos per month. Every video is up to 60 seconds; a longer video counts as 2.
- Paid pilot: $149 for 3 videos (`/sample-edit`). A free 15-second watermarked sample is included with the pilot — never call the pilot itself free, never say "free trial".
- Same-day / rush editing exists; price is quoted on a call (WhatsApp, email hello@brandexvideo.com, or the contact form). Never invent a rush price.
- Includes: colour grading, animated captions, background music, thumbnails, unlimited revisions, 24-hour standard turnaround, direct publishing to the client's accounts.
- Author on every post: Shankar, Creative Director.

## Hard rules
1. **Never name real creators, influencers or public figures** (no "Hormozi-style", no "MrBeast-style"). Describe styles instead: "bold-caption style", "cinematic talking-head style". `scripts/check.py` blocks a list of names; the rule covers names not on the list too.
2. No competitor-comparison posts ("X vs ShortVids", "best alternatives to ..."). Generic model comparisons (freelancer vs agency vs subscription) are fine.
3. No prices in rupees, no "Indian clients", no "virtual US address". Audience is overseas only.
4. No fabricated statistics. Use a number only if you found it on a credible page during research this run; otherwise write it qualitatively. Figures about BrandexVideo pricing come only from the list above.
5. SEO title ≤ 58 characters before the automatic " | BrandexVideo" suffix. Meta description 120–160 characters, answer-first, contains the primary keyword.
6. Answer-first: the `lead` paragraph must directly answer the query of the primary keyword in 2–3 sentences with the key figure in `<strong>`.
7. Length 900–1,300 words of body (lead + body). 4–6 H2 sections that each match a real sub-question. One `<table>` or one `<div class="callout">` where it genuinely helps.
8. 4–6 FAQs that are real "People also ask" style questions; each answer 1–3 sentences, self-contained (they go into FAQPage schema).
9. Internal links: include every link target listed on the keyword line, plus at least one other relevant /for/, /services/ or /blog/ page. Only link to pages that exist in the repo (check.py verifies).
10. CTA at the end: default `{"h2":"Try us on 3 videos first","p":"The $149 pilot: 3 edited videos in 3 days, plus a free 15-second watermarked sample before you pay.","btn":"Start the $149 pilot →","href":"/sample-edit"}`. For pricing posts use href `/#pricing` and btn "View BrandexVideo pricing →".
11. Tone: direct, specific, practical. Short paragraphs (≤ 3 sentences). British/US spelling consistent within a post (either is fine). No filler intros, no "In today's digital landscape".
12. Dates: `date` is today's date in Asia/Kolkata.

## Allowed HTML inside `body`
`<h2>`, `<h3>`, `<p>`, `<strong>`, `<em>`, `<a href="/...">`, `<ul>/<ol>/<li>`, `<table><thead><tr><th>…</th></tr></thead><tbody><tr><td>…</td></tr><tr class="hl">…</tr></tbody></table>`, `<div class="callout"><div class="callout-title">…</div><p>…</p></div>`. Nothing else (no images, no scripts, no inline styles).

## Run procedure (every scheduled run)
1. Attach and clone `behindtalkies/brandexvideo-site` (push access). Work on `main`.
2. Open `content/keyword-queue.md`. Take the first `- [ ]` line (two lines if the run is a 2-post run). Parse slug, keyword, H1, category, link targets.
3. Research the keyword with 3–5 web searches: current SERP intent, People-also-ask questions, any 2026 figures worth citing, what the top results miss. Spend most of the effort on the content, not the research.
4. Write the spec JSON to `content/drafts/<slug>.json` with all fields in `scripts/new_post.py`'s docstring.
5. Run `python3 scripts/new_post.py content/drafts/<slug>.json` — it builds `blog/<slug>.html`, adds the card to `blog/index.html`, updates `sitemap.xml` and `llms.txt`.
6. Run `python3 scripts/check.py`. Fix anything it flags and re-run until `ALL CHECKS PASSED`. Never push with failures.
7. Mark the queue line `- [x] YYYY-MM-DD` (keep the rest of the line).
8. `git add -A && git commit -m "Blog: <H1>" && git push origin main`. Netlify deploys automatically.
9. After pushing, wait 90 seconds and fetch `https://www.brandexvideo.com/blog/<slug>` to confirm it is live (HTTP 200 and the H1 present). If not live after a second check 2 minutes later, report it.
10. Final message: post title, live URL, primary keyword, internal links used, and the next queued keyword. Nothing else.

## If something is wrong
- Queue empty → write 10 new queue lines in the same format following the section themes (money questions, hire how-tos, technique, industry guides, geo, platform), commit them, then proceed with the first one.
- `new_post.py` or `check.py` errors → fix the spec, not the scripts. Only edit the scripts if they themselves are broken, and say so in the final message.
- Git push rejected → `git pull --rebase origin main` and push again, once.
