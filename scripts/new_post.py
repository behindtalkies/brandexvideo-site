#!/usr/bin/env python3
"""
Build a BrandexVideo blog post from a JSON spec and wire it into the site.

Usage:  python3 scripts/new_post.py content/drafts/<slug>.json

Spec (JSON) fields:
  slug          "why-dentists-need-reels"            (lowercase, hyphens; becomes /blog/<slug>)
  seo_title     "<=58 chars>"                         ("| BrandexVideo" is appended automatically; total must be <=65)
  h1            "Why Dentists Are Winning Patients With Reels in 2026"
  description   "140-160 chars, answer-first, contains the keyword"
  category      "Personal Brand" | "Pricing Guide" | "Editing Technique" | "Buying Guide" | "Process" | "Platform Guide" | "Industry Guide"
  date          "2026-10-15"                         (ISO; display + schema derived from it)
  read_min      6
  lead          "<p>-less HTML for the answer-first lead (may contain <strong>)"
  body          "HTML: <h2>, <h3>, <p>, <ul>, <ol>, <table>, <div class=\"callout\">..."
  faqs          [{"q": "...", "a": "..."}, ...]        (4-6; plain text, no HTML)
  cta           {"h2": "...", "p": "...", "btn": "Start the $149 pilot →", "href": "/sample-edit"}
  card_blurb    "1-2 sentence blurb for the blog index card (plain text)"
  llms_blurb    "One-line summary for llms.txt (plain text, with the key fact)"

What it does:
  1. Writes blog/<slug>.html using the exact head/CSS/nav/footer of the existing posts
     with BlogPosting + BreadcrumbList + FAQPage schema.
  2. Inserts a card at the TOP of blog/index.html.
  3. Adds a <url> entry to sitemap.xml and refreshes /blog/ lastmod.
  4. Appends a line under "## Blog" in llms.txt.
Idempotent: re-running for the same slug replaces the post and does not duplicate the card/sitemap/llms lines.
"""
import json, re, sys, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://www.brandexvideo.com"
TEMPLATE = ROOT / "blog" / "short-form-video-editing-cost-2026.html"

def esc(s): return html.escape(s, quote=True)

def main(spec_path):
    spec = json.load(open(spec_path))
    for k in ["slug","seo_title","h1","description","category","date","read_min","lead","body","faqs","cta","card_blurb","llms_blurb"]:
        if k not in spec: sys.exit(f"spec missing: {k}")
    slug = spec["slug"]
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug), "bad slug"
    url = f"{BASE}/blog/{slug}"
    title = f'{spec["seo_title"].strip()} | BrandexVideo'
    assert len(title) <= 65, f"title too long ({len(title)}): {title}"
    desc = spec["description"].strip()
    assert 110 <= len(desc) <= 165, f"description length {len(desc)} (want 110-165)"
    d = datetime.date.fromisoformat(spec["date"])
    date_long = d.strftime("%-d %B %Y"); date_short = d.strftime("%-d %b %Y")
    faqs = spec["faqs"]; assert 3 <= len(faqs) <= 7

    tpl = open(TEMPLATE, encoding="utf-8").read()
    css = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
    nav = re.search(r"<nav class=\"nav\">.*?</nav>", tpl, re.S).group(0)
    tail = tpl[tpl.find("</article></main>"):]  # askai + footer + closing tags

    schema = {"@context":"https://schema.org","@graph":[
      {"@type":"BlogPosting","@id":url+"#article","headline":spec["h1"],"description":desc,
       "datePublished":spec["date"],"dateModified":spec["date"],"inLanguage":"en",
       "mainEntityOfPage":{"@type":"WebPage","@id":url},
       "author":{"@type":"Person","name":"Shankar","jobTitle":"Creative Director","worksFor":{"@type":"Organization","name":"BrandexVideo"}},
       "publisher":{"@type":"Organization","name":"BrandexVideo","url":BASE+"/","logo":{"@type":"ImageObject","url":BASE+"/img/logo.png"}},
       "image":BASE+"/img/logo.png","articleSection":spec["category"],"wordCount":len(re.sub(r"<[^>]+>"," ",spec["lead"]+spec["body"]).split()),
       "speakable":{"@type":"SpeakableSpecification","cssSelector":["h1",".lead"]}},
      {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":"Blog","item":BASE+"/blog/"},
        {"@type":"ListItem","position":3,"name":spec["h1"],"item":url}]},
      {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in faqs]}
    ]}
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")

    head = (
      '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
      f'<title>{esc(title)}</title>\n'
      f'<meta name="description" content="{esc(desc)}">\n'
      '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">\n'
      f'<link rel="canonical" href="{url}">\n'
      f'<meta property="og:type" content="article"><meta property="og:site_name" content="BrandexVideo"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}/img/logo.png">\n'
      f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}">\n'
      '<meta name="theme-color" content="#7C3AED">\n'
      '<link rel="icon" type="image/png" href="/img/favicon.png">\n'
      '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
      '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"></noscript>\n'
      f'<script type="application/ld+json">\n{schema_json}\n</script>\n'
      f'{css}</head><body>{nav}\n'
    )
    faq_html = "\n".join(
      f'<details{" open" if i==0 else ""}><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>' for i,f in enumerate(faqs))
    cta = spec["cta"]
    article = (
      '<main class="wrap"><article>\n'
      f'<span class="eyebrow">{esc(spec["category"])} · {d.year}</span>\n'
      f'<h1>{esc(spec["h1"])}</h1>\n'
      f'<div class="meta"><span>✍️ Shankar, Creative Director</span><span>📅 {date_long}</span><span>⏱ {int(spec["read_min"])} min read</span></div>\n\n'
      f'<p class="lead">{spec["lead"].strip()}</p>\n\n'
      f'{spec["body"].strip()}\n\n'
      '<h2>Frequently asked questions</h2>\n<div class="faq">\n' + faq_html + '\n</div>\n\n'
      f'<div class="cta">\n<h2>{esc(cta["h2"])}</h2>\n<p>{esc(cta["p"])}</p>\n<a href="{esc(cta["href"])}" class="btn">{esc(cta["btn"])}</a>\n</div>\n\n'
      '<div class="author">\n<div class="author-av">S</div>\n<div><div class="author-name">Shankar</div><div class="author-role">Creative Director, BrandexVideo · Edits short-form content for creators in the USA, UK and UAE</div></div>\n</div>\n'
    )
    out = ROOT / "blog" / f"{slug}.html"
    out.write_text(head + article + tail, encoding="utf-8")

    # ---- blog index card (top of list) ----
    idx_p = ROOT / "blog" / "index.html"; idx = idx_p.read_text(encoding="utf-8")
    idx = re.sub(rf'<a href="/blog/{re.escape(slug)}" class="post">.*?</a>', "", idx, flags=re.S)
    card = (f'<a href="/blog/{slug}" class="post"><span class="post-cat">{esc(spec["category"])}</span>'
            f'<h2>{esc(spec["h1"])}</h2><p>{esc(spec["card_blurb"].strip())}</p>'
            f'<span class="post-meta">{date_short} · {int(spec["read_min"])} min read</span></a>')
    assert '<div class="posts">' in idx
    idx = idx.replace('<div class="posts">', '<div class="posts">' + card, 1)
    idx_p.write_text(idx, encoding="utf-8")

    # ---- sitemap ----
    sm_p = ROOT / "sitemap.xml"; sm = sm_p.read_text(encoding="utf-8")
    sm = re.sub(rf"\s*<url>\s*<loc>{re.escape(url)}</loc>.*?</url>", "", sm, flags=re.S)
    entry = (f"\n  <url>\n    <loc>{url}</loc>\n    <lastmod>{spec['date']}</lastmod>\n"
             f"    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>")
    sm = sm.replace("</urlset>", entry.lstrip("\n") + "\n</urlset>")
    sm = re.sub(r"(<loc>https://www\.brandexvideo\.com/blog/</loc>\s*<lastmod>)[^<]+", rf"\g<1>{spec['date']}", sm)
    sm_p.write_text(sm, encoding="utf-8")

    # ---- llms.txt ----
    ll_p = ROOT / "llms.txt"; ll = ll_p.read_text(encoding="utf-8")
    ll = "\n".join(l for l in ll.split("\n") if f"]({url})" not in l)
    line = f"- [{spec['h1']}]({url}): {spec['llms_blurb'].strip()}"
    m = re.search(r"^## Blog\s*\n(?:.*\n)*?(?=\n## |\Z)", ll, re.M)
    if m:
        block = m.group(0).rstrip("\n") + "\n" + line + "\n"
        ll = ll[:m.start()] + block + ll[m.end():]
    else:
        ll = ll.rstrip("\n") + "\n\n## Blog\n" + line + "\n"
    ll_p.write_text(ll, encoding="utf-8")
    print(f"OK  {url}")

if __name__ == "__main__":
    main(sys.argv[1])
