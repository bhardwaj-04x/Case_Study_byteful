"""
generate_pages.py
Reads case-study-input-sheet.csv and produces one WordPress-safe HTML file
per case study.

WordPress instructions (printed inside each generated file):
  1. Add FA CDN link to Appearance > Theme Options > Custom Code (head):
       <link rel="stylesheet"
             href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  2. Open the WordPress page, add a Custom HTML block.
  3. Paste ONLY the content between the WORDPRESS PASTE START / END markers.
"""

import csv
import re
from pathlib import Path
from string import Template          # uses $var syntax — no curly-brace collision

CSV_FILE = Path(r'C:\Users\prana\OneDrive\Desktop\CaseStudyByteful\case-study-input-sheet.csv')

# ── Icon lookup ───────────────────────────────────────────────────────────────
def platform_icon(platform):
    p = platform.lower()
    if 'netsuite'   in p: return 'fa-solid fa-cloud'
    if 'salesforce' in p: return 'fa-solid fa-cloud-bolt'
    if 'graphql'    in p: return 'fa-solid fa-diagram-project'
    if 'react'      in p: return 'fa-brands fa-react'
    if 'python'     in p: return 'fa-brands fa-python'
    if 'node'       in p: return 'fa-brands fa-node-js'
    if 'mongo'      in p: return 'fa-solid fa-database'
    if 'postgres'   in p: return 'fa-solid fa-database'
    if 'lwc'        in p: return 'fa-solid fa-bolt'
    return 'fa-solid fa-layer-group'


# ── Content helpers ───────────────────────────────────────────────────────────
def make_tech_chips(platform):
    parts = [p.strip() for p in re.split(r'[,/\n]', platform) if p.strip()]
    return '\n'.join(f'<span class="cs-chip">{c}</span>' for c in parts[:8])


def section_bullets(text):
    """Return list of {title, body} dicts for lines like 'Heading: detail'."""
    pattern = re.compile(r'^(.+?):\s*(.+)$')
    cards = []
    for line in text.split('\n'):
        m = pattern.match(line.strip())
        if m:
            cards.append({'title': m.group(1).strip(), 'body': m.group(2).strip()})
    return cards


def make_challenge_cards(text):
    cards = section_bullets(text)
    if not cards:
        paras = [p.strip() for p in text.split('\n\n') if p.strip()]
        return '\n'.join(f'<p class="cs-prose">{p}</p>' for p in paras[:4])
    rows = []
    for c in cards[:6]:
        rows.append(
            f'<div class="cs-card cs-card--challenge">'
            f'<h4>{c["title"]}</h4><p>{c["body"]}</p>'
            f'</div>'
        )
    return '<div class="cs-grid cs-grid--3">\n' + '\n'.join(rows) + '\n</div>'


def make_solution_cards(text):
    cards = section_bullets(text)
    if not cards:
        # Numbered list fallback
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        items = [re.sub(r'^[\d+\.\-\*•]\s*', '', l) for l in lines if l]
        if items:
            lis = '\n'.join(f'<li>{i}</li>' for i in items[:10])
            return f'<ul class="cs-prose">{lis}</ul>'
        return f'<p class="cs-prose">{text}</p>'

    rows = []
    for c in cards[:6]:
        rows.append(
            f'<div class="cs-card cs-card--solution">'
            f'<div class="cs-card__icon"><i class="fa-solid fa-check"></i></div>'
            f'<div><h4>{c["title"]}</h4><p>{c["body"]}</p></div>'
            f'</div>'
        )
    return '<div class="cs-grid cs-grid--2">\n' + '\n'.join(rows) + '\n</div>'


def make_story_block(story):
    if not story or not story.strip():
        return ''
    paras = [p.strip() for p in story.split('\n\n') if p.strip()]
    inner = '\n'.join(f'<p class="cs-prose">{p}</p>' for p in paras[:3])
    return (
        '<div class="cs-section">'
        '<div class="cs-inner">'
        '<span class="cs-section__eyebrow">Overview</span>'
        '<h2 class="cs-section__title">Background</h2>'
        + inner +
        '</div></div>'
    )


def derive_hero_title(customer, problem):
    first = problem.strip().split('\n')[0].strip()
    if ':' in first:
        topic = first.split(':')[0].strip()
    else:
        topic = ' '.join(first.split()[:8])
    return f"{customer}: {topic}"


def derive_conclusion(customer, platform_short, solution):
    first = solution.strip().split('\n')[0].strip()[:120]
    return (
        f"By partnering with Byteful, {customer} transformed their operations "
        f"using {platform_short}. {first}. "
        f"The result was a scalable, reliable system that reduced manual overhead "
        f"and delivered measurable business value."
    )


# ── CSS (written as a plain string — no Python format placeholders) ───────────
CSS = """\
<style>
/* All rules are scoped under .cs-pro — zero bleed into the WordPress theme */
.cs-pro {
  --cs-red:    #E90004;
  --cs-black:  #0b0b0b;
  --cs-dark:   #1a1a1a;
  --cs-white:  #ffffff;
  --cs-muted:  #555555;
  --cs-light:  #f7f8fc;
  --cs-border: #e5e7eb;
  font-family: inherit;
  color: #111111;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}

/* ── Hero ─────────────────────────────────────────────────────── */
.cs-pro .cs-hero {
  position: relative;
  padding: 90px 24px 80px;
  background: var(--cs-black);
  text-align: center;
  overflow: hidden;
}
.cs-pro .cs-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(233,0,4,.18) 0%, transparent 60%);
  pointer-events: none;
}
.cs-pro .cs-hero__badge {
  display: inline-block;
  margin-bottom: 20px;
  padding: 5px 18px;
  border: 1px solid var(--cs-red);
  border-radius: 999px;
  color: var(--cs-red);
  font-size: 11px;
  letter-spacing: 2.5px;
  text-transform: uppercase;
}
.cs-pro .cs-hero__title {
  position: relative;
  margin: 0 auto 18px;
  max-width: 860px;
  font-size: clamp(1.75rem, 4vw, 3rem);
  font-weight: 800;
  color: var(--cs-white);
  line-height: 1.15;
}
.cs-pro .cs-hero__sub {
  position: relative;
  margin: 0 auto;
  max-width: 620px;
  font-size: clamp(0.95rem, 2vw, 1.1rem);
  color: rgba(255,255,255,.72);
}

/* ── Info bar ─────────────────────────────────────────────────── */
.cs-pro .cs-infobar {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  padding: 20px 24px;
  background: var(--cs-white);
  border-bottom: 1px solid var(--cs-border);
}
.cs-pro .cs-infobar__item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1 1 220px;
  min-width: 200px;
  max-width: 320px;
  padding: 12px 16px;
  border: 1px solid var(--cs-border);
  border-radius: 10px;
  background: var(--cs-white);
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
  transition: border-color .25s, transform .25s;
}
.cs-pro .cs-infobar__item:hover {
  border-color: var(--cs-red);
  transform: translateY(-2px);
}
.cs-pro .cs-infobar__icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
  background: rgba(233,0,4,.09);
  color: var(--cs-red);
  font-size: 1rem;
}
.cs-pro .cs-infobar__label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--cs-muted);
  margin-bottom: 2px;
}
.cs-pro .cs-infobar__value {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--cs-black);
}

/* ── Sections ─────────────────────────────────────────────────── */
.cs-pro .cs-section {
  width: 100%;
  padding: 72px 24px;
  background: var(--cs-white);
}
.cs-pro .cs-section--alt  { background: var(--cs-light); }
.cs-pro .cs-inner {
  max-width: 1180px;
  margin: 0 auto;
}
.cs-pro .cs-section__eyebrow {
  display: inline-block;
  margin-bottom: 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--cs-red);
}
.cs-pro .cs-section__title {
  margin: 0 0 28px;
  font-size: clamp(1.35rem, 3vw, 2rem);
  font-weight: 800;
  color: var(--cs-black);
  line-height: 1.2;
}
.cs-pro .cs-section__title::after {
  content: '';
  display: block;
  margin-top: 12px;
  width: 48px;
  height: 4px;
  border-radius: 2px;
  background: var(--cs-red);
}

/* ── Cards ────────────────────────────────────────────────────── */
.cs-pro .cs-grid {
  display: grid;
  gap: 20px;
  margin-top: 8px;
}
.cs-pro .cs-grid--2 { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.cs-pro .cs-grid--3 { grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }

.cs-pro .cs-card {
  padding: 26px;
  border: 1px solid var(--cs-border);
  border-radius: 14px;
  background: var(--cs-white);
  box-shadow: 0 8px 24px rgba(0,0,0,.05);
  transition: border-color .25s, transform .3s, box-shadow .3s;
}
.cs-pro .cs-card:hover {
  border-color: var(--cs-red);
  transform: translateY(-5px);
  box-shadow: 0 16px 40px rgba(233,0,4,.12);
}
.cs-pro .cs-card h4 {
  margin: 0 0 10px;
  font-size: 1rem;
  font-weight: 700;
  color: var(--cs-black);
}
.cs-pro .cs-card p {
  margin: 0;
  font-size: 0.93rem;
  color: var(--cs-muted);
  line-height: 1.7;
}
.cs-pro .cs-card--challenge {
  border-top: 3px solid var(--cs-red);
}
.cs-pro .cs-card--solution {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.cs-pro .cs-card__icon {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--cs-red), var(--cs-dark));
  color: var(--cs-white);
  font-size: 0.9rem;
}

/* ── Prose ────────────────────────────────────────────────────── */
.cs-pro .cs-prose {
  color: var(--cs-muted);
  line-height: 1.85;
  max-width: 840px;
  margin-bottom: 16px;
}
.cs-pro .cs-prose ul {
  padding-left: 22px;
  margin: 0;
}
.cs-pro .cs-prose li { margin-bottom: 8px; }

/* ── Visual band ──────────────────────────────────────────────── */
.cs-pro .cs-band {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 240px;
  padding: 60px 24px;
  position: relative;
  background: var(--cs-black);
  overflow: hidden;
}
.cs-pro .cs-band::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(233,0,4,.25), transparent 60%);
  pointer-events: none;
}
.cs-pro .cs-band__inner   { position: relative; z-index: 1; }
.cs-pro .cs-band__title {
  margin: 0 0 12px;
  font-size: clamp(1.2rem, 2.5vw, 1.7rem);
  font-weight: 800;
  color: var(--cs-white);
}
.cs-pro .cs-band__sub {
  color: rgba(255,255,255,.68);
  font-size: 1rem;
  max-width: 600px;
  margin: 0 auto;
}
.cs-pro .cs-tech-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 20px;
}
.cs-pro .cs-chip {
  padding: 6px 16px;
  border: 1px solid rgba(233,0,4,.5);
  border-radius: 999px;
  color: var(--cs-red);
  background: rgba(233,0,4,.07);
  font-size: 0.82rem;
  font-weight: 600;
}

/* ── Conclusion ───────────────────────────────────────────────── */
.cs-pro .cs-conclusion {
  padding: 72px 24px;
  background: var(--cs-white);
  text-align: center;
}
.cs-pro .cs-conclusion__icon {
  font-size: 2.6rem;
  color: var(--cs-red);
  margin-bottom: 18px;
  display: block;
}
.cs-pro .cs-conclusion__title {
  margin: 0 0 18px;
  font-size: clamp(1.4rem, 3vw, 2rem);
  font-weight: 800;
  color: var(--cs-black);
}
.cs-pro .cs-conclusion__text {
  max-width: 720px;
  margin: 0 auto;
  color: var(--cs-muted);
  line-height: 1.85;
}

/* ── Responsive ───────────────────────────────────────────────── */
@media (max-width: 640px) {
  .cs-pro .cs-hero        { padding: 64px 16px 56px; }
  .cs-pro .cs-section     { padding: 48px 16px; }
  .cs-pro .cs-conclusion  { padding: 48px 16px; }
  .cs-pro .cs-infobar     { overflow-x: auto; flex-wrap: nowrap; justify-content: flex-start; }
  .cs-pro .cs-grid--2,
  .cs-pro .cs-grid--3     { grid-template-columns: 1fr; }
}
</style>"""


def build_page(cs, status_label):
    cid       = cs['id']
    customer  = cs['customer']
    developer = cs['developer']
    platform  = cs['platform']
    story     = cs['story']
    problem   = cs['problem']
    solution  = cs['solution']

    # Short platform label (max 60 chars)
    parts = [p.strip() for p in re.split(r'[,/\n]', platform) if p.strip()]
    platform_short = ', '.join(parts)
    if len(platform_short) > 60:
        platform_short = ', '.join(parts[:3]) + '…'

    icon            = platform_icon(platform)
    hero_title      = derive_hero_title(customer, problem)
    hero_sub        = (
        f"How Byteful helped {customer} solve a critical business challenge "
        f"using {platform_short}."
    )
    challenge_block = make_challenge_cards(problem)
    solution_block  = make_solution_cards(solution)
    story_block     = make_story_block(story)
    tech_chips      = make_tech_chips(platform)
    conclusion      = derive_conclusion(customer, platform_short, solution)

    body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Case Study – {customer}</title>
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
</head>
<!--
  WORDPRESS INSTRUCTIONS
  1. Add to Appearance > Theme Options > Custom Head Code (if FA not already loaded):
       <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  2. In the page editor, add a "Custom HTML" block.
  3. Paste ONLY the content between the markers below into that block.
-->

<!-- === WORDPRESS PASTE START === -->
{CSS}

<section class="cs-pro">

  <!-- HERO -->
  <div class="cs-hero">
    <span class="cs-hero__badge">
      <i class="{icon}"></i>&nbsp; Case Study
    </span>
    <h1 class="cs-hero__title">{hero_title}</h1>
    <p class="cs-hero__sub">{hero_sub}</p>
  </div>

  <!-- INFO BAR -->
  <div class="cs-infobar">
    <div class="cs-infobar__item">
      <div class="cs-infobar__icon"><i class="fa-solid fa-building"></i></div>
      <div>
        <div class="cs-infobar__label">Client</div>
        <div class="cs-infobar__value">{customer}</div>
      </div>
    </div>
    <div class="cs-infobar__item">
      <div class="cs-infobar__icon"><i class="fa-solid fa-user-tie"></i></div>
      <div>
        <div class="cs-infobar__label">Developer</div>
        <div class="cs-infobar__value">{developer}</div>
      </div>
    </div>
    <div class="cs-infobar__item">
      <div class="cs-infobar__icon"><i class="{icon}"></i></div>
      <div>
        <div class="cs-infobar__label">Tech Stack</div>
        <div class="cs-infobar__value">{platform_short}</div>
      </div>
    </div>
    <div class="cs-infobar__item">
      <div class="cs-infobar__icon"><i class="fa-solid fa-circle-check"></i></div>
      <div>
        <div class="cs-infobar__label">Status</div>
        <div class="cs-infobar__value">{status_label}</div>
      </div>
    </div>
  </div>

  {story_block}

  <!-- THE CHALLENGE -->
  <div class="cs-section cs-section--alt">
    <div class="cs-inner">
      <span class="cs-section__eyebrow">The Problem</span>
      <h2 class="cs-section__title">The Challenge</h2>
      {challenge_block}
    </div>
  </div>

  <!-- VISUAL BAND -->
  <div class="cs-band">
    <div class="cs-band__inner">
      <h3 class="cs-band__title">
        <i class="fa-solid fa-gears"></i>&nbsp; Built on Modern Technology
      </h3>
      <p class="cs-band__sub">
        Powered by {platform_short} — engineered for reliability and scale.
      </p>
      <div class="cs-tech-chips">
        {tech_chips}
      </div>
    </div>
  </div>

  <!-- THE SOLUTION -->
  <div class="cs-section">
    <div class="cs-inner">
      <span class="cs-section__eyebrow">Our Approach</span>
      <h2 class="cs-section__title">The Solution</h2>
      {solution_block}
    </div>
  </div>

  <!-- CONCLUSION -->
  <div class="cs-conclusion">
    <div class="cs-inner">
      <i class="fa-solid fa-trophy cs-conclusion__icon"></i>
      <h2 class="cs-conclusion__title">Outcome</h2>
      <p class="cs-conclusion__text">{conclusion}</p>
    </div>
  </div>

</section>
<!-- === WORDPRESS PASTE END === -->

</html>"""

    return body


# ── Run ───────────────────────────────────────────────────────────────────────
with open(CSV_FILE, encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)   # "For Reviewers…" label row
    next(reader)   # column header row

    case_studies = []
    for row in reader:
        if len(row) >= 9 and row[0].strip() and row[0].strip().isdigit():
            case_studies.append({
                'id':        row[0].strip(),
                'rating':    row[1].strip().lower(),
                'story':     row[3].strip(),
                'problem':   row[4].strip(),
                'solution':  row[5].strip(),
                'developer': row[6].strip(),
                'customer':  row[7].strip(),
                'platform':  row[8].strip(),
            })

print(f"Found {len(case_studies)} case studies")

for cs in case_studies:
    rating = cs['rating']
    if rating in ('review', 'publish'):
        label    = 'Published' if rating == 'publish' else 'In Review'
        suffix   = 'publish'   if rating == 'publish' else 'review'
        filename = f"case-study-{cs['id']}-{suffix}.html"
        html     = build_page(cs, label)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  {filename}  —  {cs['customer']}")

print("Done.")
