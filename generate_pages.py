"""
generate_pages.py
Reads case-study-input-sheet.csv → produces one WordPress-safe HTML file per study.

WordPress:
  1. Add FA CDN to Appearance › Theme Options › Custom Head Code:
       <link rel="stylesheet"
             href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  2. Add a Custom HTML block to the page.
  3. Paste ONLY the block between WORDPRESS PASTE START / END.
"""

import csv, re
from pathlib import Path

CSV_FILE = Path(r'C:\Users\prana\OneDrive\Desktop\CaseStudyByteful\case-study-input-sheet.csv')

# ─── Image library (Unsplash – free to use) ───────────────────────────────────
# Each platform key maps to {banner, metrics, process} photo IDs
IMGS = {
    'netsuite': {
        'banner' : 'photo-1460925895917-afdab827c52f',  # analytics laptop
        'metrics': 'photo-1551288049-bebda4e38f71',     # dashboard screen
        'process': 'photo-1519389950473-47ba0277781c',  # team laptops
    },
    'salesforce': {
        'banner' : 'photo-1553877522-43269d4ea984',     # cloud tech
        'metrics': 'photo-1552664730-d307ca884978',     # business meeting
        'process': 'photo-1507003211169-0a1dd7228f2d',  # person at work
    },
    'graphql': {
        'banner' : 'photo-1558494949-ef010cbdcc31',     # server room
        'metrics': 'photo-1544197150-b99a580bb7a8',     # data center
        'process': 'photo-1518770660439-4636190af475',  # circuit board
    },
    'python': {
        'banner' : 'photo-1504868584819-f8e8b4b6d7e3',  # charts / analytics
        'metrics': 'photo-1460925895917-afdab827c52f',  # data screen
        'process': 'photo-1498050108023-c5249f4df085',  # coding laptop
    },
    'react': {
        'banner' : 'photo-1547658719-da2b51169166',     # web design
        'metrics': 'photo-1498050108023-c5249f4df085',  # coding
        'process': 'photo-1519389950473-47ba0277781c',  # team
    },
    'default': {
        'banner' : 'photo-1518770660439-4636190af475',  # circuit board
        'metrics': 'photo-1558494949-ef010cbdcc31',     # server room
        'process': 'photo-1460925895917-afdab827c52f',  # analytics
    },
}

def pick_imgs(platform):
    p = platform.lower()
    for key in ('netsuite', 'salesforce', 'graphql', 'python', 'react'):
        if key in p:
            return IMGS[key]
    return IMGS['default']

def img_url(photo_id, w=1200, q=80):
    return f'https://images.unsplash.com/{photo_id}?w={w}&q={q}&fit=crop&auto=format'


# ─── Platform icon ────────────────────────────────────────────────────────────
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


# ─── Metrics derivation ───────────────────────────────────────────────────────
def derive_metrics(problem, solution, platform):
    """Pull up to 4 key numbers from text; fall back to meaningful defaults."""
    text  = problem + ' ' + solution
    found = []

    m = re.search(r'(\d+)\s*[\-–]\s*(\d+)\s*hours?', text, re.I)
    if m:
        found.append({'num': f'{m.group(2)}hrs', 'label': 'Hours Saved / Month',
                      'icon': 'fa-solid fa-clock'})

    m = re.search(r'(\d+)\s*GB', text, re.I)
    if m:
        found.append({'num': f'{m.group(1)} GB', 'label': 'Data Processed',
                      'icon': 'fa-solid fa-database'})

    m = re.search(r'(\d+)\s*(?:months?|years?)', text, re.I)
    if m:
        unit = 'Month' if 'month' in m.group(0).lower() else 'Year'
        found.append({'num': m.group(1), 'label': f'Delivery ({unit}s)',
                      'icon': 'fa-solid fa-calendar-check'})

    m = re.search(r'(\d+)\s*(?:databases?|APIs?|endpoints?)', text, re.I)
    if m:
        label = ('Databases Unified' if 'database' in m.group(0).lower()
                 else 'API Endpoints')
        found.append({'num': m.group(1), 'label': label,
                      'icon': 'fa-solid fa-diagram-project'})

    # Fill to 4 with generic but meaningful defaults
    defaults = [
        {'num': '100%', 'label': 'Automated',        'icon': 'fa-solid fa-robot'},
        {'num': '0',    'label': 'Manual Errors',     'icon': 'fa-solid fa-shield-halved'},
        {'num': '24/7', 'label': 'System Uptime',     'icon': 'fa-solid fa-server'},
        {'num': '↑',    'label': 'Business Growth',   'icon': 'fa-solid fa-chart-line'},
    ]
    for d in defaults:
        if len(found) >= 4:
            break
        found.append(d)

    return found[:4]


# ─── Content helpers ──────────────────────────────────────────────────────────
def make_tech_chips(platform):
    parts = [p.strip() for p in re.split(r'[,/\n]', platform) if p.strip()]
    return '\n'.join(f'<span class="cs-chip">{c}</span>' for c in parts[:8])

def section_bullets(text):
    pattern = re.compile(r'^(.+?):\s*(.+)$')
    return [{'title': m.group(1).strip(), 'body': m.group(2).strip()}
            for line in text.split('\n') if (m := pattern.match(line.strip()))]

def make_challenge_html(text):
    cards  = section_bullets(text)
    paras  = [p.strip() for p in text.split('\n\n') if p.strip()]
    intro  = paras[0] if paras else ''
    if cards:
        items = '\n'.join(f'''<li class="cs-chal-item">
  <span class="cs-chal-dot"></span>
  <div><strong>{c["title"]}</strong><p>{c["body"]}</p></div>
</li>''' for c in cards[:6])
    else:
        lines = [re.sub(r'^[\d+\.\-\*•]\s*', '', l.strip()) for l in text.split('\n') if l.strip()]
        items = '\n'.join(f'''<li class="cs-chal-item">
  <span class="cs-chal-dot"></span>
  <div><p>{l}</p></div>
</li>''' for l in lines[:6])
    return f'''<div class="cs-split">
  <div class="cs-split__left"><p class="cs-lead">{intro}</p></div>
  <div class="cs-split__right"><ul class="cs-chal-list">{items}</ul></div>
</div>'''

def make_solution_html(text):
    cards = section_bullets(text)
    if not cards:
        raw   = [re.sub(r'^[\d+\.\-\*•]\s*', '', l.strip()) for l in text.split('\n') if l.strip()]
        cards = [{'title': '', 'body': l} for l in raw[:6]]
    return '\n'.join(f'''<div class="cs-step">
  <div class="cs-step__num">{i:02d}</div>
  <div class="cs-step__body">
    {"<h4>"+s["title"]+"</h4>" if s["title"] else ""}
    <p>{s["body"]}</p>
  </div>
</div>''' for i, s in enumerate(cards[:6], 1))

def make_story_block(story):
    if not story or not story.strip():
        return ''
    paras = [p.strip() for p in story.split('\n\n') if p.strip()]
    inner = '\n'.join(f'<p class="cs-lead">{p}</p>' for p in paras[:2])
    return f'''<div class="cs-section">
  <div class="cs-inner cs-overview">
    <div class="cs-overview__tag"><span class="cs-eyebrow">Project Overview</span></div>
    <div class="cs-overview__body">{inner}</div>
  </div>
</div>'''

def derive_hero_sub(problem):
    first = problem.strip().split('\n')[0].strip()
    words = first.split()[:14]
    return ' '.join(words) + ('…' if len(first.split()) > 14 else '')

def derive_banner_quote(problem, solution):
    """Pick the most quotable sentence from problem or solution."""
    for text in (solution, problem):
        for sent in re.split(r'(?<=[.!?])\s+', text.strip()):
            sent = sent.strip()
            if 30 < len(sent) < 160 and not sent[0].isdigit():
                return sent
    return problem.strip().split('\n')[0][:140]

def derive_conclusion(customer, platform_short, solution):
    first = solution.strip().split('\n')[0].strip()[:140]
    return (
        f"By partnering with Byteful, {customer} transformed their operations using "
        f"{platform_short}. {first}. The result was a scalable, reliable system that "
        f"reduced manual overhead and delivered measurable business value."
    )

def make_deliverables(solution):
    """Generate 3 deliverable cards from the solution text."""
    cards = section_bullets(solution)
    if len(cards) >= 3:
        picks = cards[:3]
    else:
        lines = [re.sub(r'^[\d+\.\-\*•]\s*', '', l.strip()) for l in solution.split('\n') if l.strip()]
        picks = [{'title': '', 'body': l} for l in lines[:3]]

    icons  = ['fa-solid fa-check-circle', 'fa-solid fa-gears', 'fa-solid fa-chart-line']
    colors = ['#E90004', '#0b0b0b', '#333']
    html   = ''
    for i, (p, icon, col) in enumerate(zip(picks, icons, colors)):
        title = p['title'] or f'Deliverable {i+1}'
        body  = p['body']
        html += f'''<div class="cs-deliv-card">
  <div class="cs-deliv-card__icon" style="background:{col}">
    <i class="{icon}"></i>
  </div>
  <h4>{title}</h4>
  <p>{body}</p>
</div>\n'''
    return html


# ─── CSS ─────────────────────────────────────────────────────────────────────
CSS = """\
<style>
/* ============================================================
   BYTEFUL CASE STUDY STYLES  v3
   All rules scoped under .cs-pro — zero bleed into WP theme
   ============================================================ */
.cs-pro {
  --r:  #E90004;
  --bk: #0b0b0b;
  --dk: #181818;
  --wh: #ffffff;
  --mu: #5a5a5a;
  --lt: #f5f6fa;
  --bd: #e4e6ef;
  font-family: inherit;
  color: #111;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  width: 100%;
}
.cs-pro *, .cs-pro *::before, .cs-pro *::after { box-sizing: border-box; }
.cs-pro ul, .cs-pro ol { list-style: none; padding: 0; margin: 0; }
.cs-pro p  { margin: 0; }
.cs-pro h2, .cs-pro h3, .cs-pro h4 { margin: 0; }
.cs-pro img { max-width: 100%; height: auto; display: block; }

.cs-inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 24px;
}
.cs-eyebrow {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 800;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--r);
}

/* ── Hero ──────────────────────────────────────────────────── */
.cs-pro .cs-hero {
  position: relative;
  padding: 120px 24px 110px;
  background: var(--bk);
  overflow: hidden;
  width: 100%;
  /* subtle dot-grid texture */
  background-image:
    radial-gradient(rgba(255,255,255,.07) 1px, transparent 1px);
  background-size: 28px 28px;
}
/* red glow bar on left edge */
.cs-pro .cs-hero::after {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 6px;
  background: var(--r);
  box-shadow: 0 0 48px 4px rgba(233,0,4,.55);
}
/* layered red glows */
.cs-pro .cs-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 55% 75% at 88% 50%, rgba(233,0,4,.18), transparent),
    radial-gradient(ellipse 35% 55% at 4%  80%, rgba(233,0,4,.10), transparent);
  pointer-events: none;
}
.cs-pro .cs-hero__inner {
  position: relative;
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 48px;
}
/* filled red badge */
.cs-pro .cs-hero__badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 28px;
  padding: 9px 20px;
  border-radius: 4px;
  background: var(--r);
  color: var(--wh);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 3px;
  text-transform: uppercase;
}
.cs-pro .cs-hero__title {
  font-size: clamp(2.4rem, 5.5vw, 4.2rem);
  font-weight: 900;
  color: var(--wh);
  line-height: 1.05;
  letter-spacing: -2px;
  margin-bottom: 24px;
}
.cs-pro .cs-hero__title span { color: var(--r); }
/* red underline accent on title */
.cs-pro .cs-hero__title::after {
  content: '';
  display: block;
  width: 64px;
  height: 5px;
  background: var(--r);
  border-radius: 3px;
  margin-top: 18px;
}
.cs-pro .cs-hero__sub {
  font-size: clamp(1rem, 2vw, 1.2rem);
  color: rgba(255,255,255,.72);
  max-width: 560px;
  line-height: 1.75;
}
.cs-pro .cs-hero__card {
  flex-shrink: 0;
  width: 220px;
  padding: 28px 24px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px;
  backdrop-filter: blur(4px);
}
.cs-pro .cs-hero__card-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.cs-pro .cs-hero__card-row:last-child { border-bottom: none; }
.cs-pro .cs-hero__card-icon {
  width: 34px; height: 34px;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(233,0,4,.15);
  color: var(--r);
  border-radius: 8px;
  font-size: 0.85rem;
}
.cs-pro .cs-hero__card-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: rgba(255,255,255,.4);
  margin-bottom: 3px;
}
.cs-pro .cs-hero__card-value {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--wh);
}

/* ── Section base ──────────────────────────────────────────── */
.cs-pro .cs-section         { padding: 80px 0; background: var(--wh); }
.cs-pro .cs-section--alt    { background: var(--lt); }
.cs-pro .cs-section--dark   { background: var(--bk); }
.cs-pro .cs-section__head {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 48px;
}
.cs-pro .cs-section__num {
  font-size: 4rem;
  font-weight: 900;
  color: rgba(233,0,4,.12);
  line-height: 1;
  flex-shrink: 0;
  margin-top: -8px;
}
.cs-pro .cs-section__title {
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 900;
  color: var(--bk);
  line-height: 1.1;
  letter-spacing: -0.5px;
}
.cs-pro .cs-section--dark .cs-section__title { color: var(--wh); }
.cs-pro .cs-section__rule {
  width: 44px; height: 4px;
  background: var(--r);
  border-radius: 2px;
  margin-top: 10px;
}

/* ── Overview ──────────────────────────────────────────────── */
.cs-pro .cs-overview {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 48px;
  align-items: start;
}
.cs-pro .cs-overview__tag { padding-top: 6px; }
.cs-pro .cs-overview__body .cs-lead {
  color: var(--mu);
  line-height: 1.85;
  margin-bottom: 16px;
}

/* ── Challenge split ───────────────────────────────────────── */
.cs-pro .cs-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  align-items: start;
}
.cs-pro .cs-lead { color: var(--mu); line-height: 1.85; }
.cs-pro .cs-chal-list { display: flex; flex-direction: column; }
.cs-pro .cs-chal-item {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  padding: 20px 0;
  border-bottom: 1px solid var(--bd);
}
.cs-pro .cs-chal-item:last-child { border-bottom: none; }
.cs-pro .cs-chal-dot {
  width: 10px; height: 10px;
  flex-shrink: 0;
  margin-top: 6px;
  border-radius: 50%;
  background: var(--r);
}
.cs-pro .cs-chal-item strong {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: var(--bk);
  margin-bottom: 4px;
}
.cs-pro .cs-chal-item p { color: var(--mu); line-height: 1.65; }

/* ── ★ IMAGE BANNER ────────────────────────────────────────── */
.cs-pro .cs-imgbanner {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: center;
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  overflow: hidden;
}
.cs-pro .cs-imgbanner__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg,
    rgba(10,10,10,.88) 0%,
    rgba(10,10,10,.65) 50%,
    rgba(233,0,4,.35) 100%);
}
.cs-pro .cs-imgbanner__content {
  position: relative;
  z-index: 1;
  max-width: 1160px;
  margin: 0 auto;
  padding: 80px 24px;
}
.cs-pro .cs-imgbanner__label {
  font-size: 10.5px;
  font-weight: 800;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--r);
  margin-bottom: 18px;
}
.cs-pro .cs-imgbanner__quote {
  max-width: 740px;
  font-size: clamp(1.3rem, 3vw, 2rem);
  font-weight: 800;
  color: var(--wh);
  line-height: 1.35;
  border-left: 4px solid var(--r);
  padding-left: 28px;
  margin: 0;
}

/* ── ★ METRICS ROW ─────────────────────────────────────────── */
.cs-pro .cs-metrics-section {
  background: var(--bk);
  padding: 80px 0;
}
.cs-pro .cs-metrics-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  align-items: stretch;
}
.cs-pro .cs-metrics-img {
  position: relative;
  min-height: 360px;
  background-size: cover;
  background-position: center;
  overflow: hidden;
}
.cs-pro .cs-metrics-img::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, rgba(10,10,10,.5), transparent);
}
.cs-pro .cs-metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: rgba(255,255,255,.07);
}
.cs-pro .cs-metric-box {
  padding: 40px 32px;
  background: var(--bk);
  text-align: center;
  transition: background .25s;
}
.cs-pro .cs-metric-box:hover { background: #111; }
.cs-pro .cs-metric-box__num {
  display: block;
  font-size: clamp(2.2rem, 5vw, 3.4rem);
  font-weight: 900;
  color: var(--r);
  line-height: 1;
  margin-bottom: 10px;
}
.cs-pro .cs-metric-box__icon {
  display: block;
  font-size: 1.1rem;
  color: rgba(233,0,4,.5);
  margin-bottom: 10px;
}
.cs-pro .cs-metric-box__label {
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: rgba(255,255,255,.5);
}

/* ── Platform band ─────────────────────────────────────────── */
.cs-pro .cs-band {
  padding: 72px 24px;
  background: var(--bk);
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cs-pro .cs-band::before {
  content: '';
  position: absolute;
  left: -200px; top: -200px;
  width: 500px; height: 500px;
  border-radius: 50%;
  background: rgba(233,0,4,.07);
  filter: blur(60px);
  pointer-events: none;
}
.cs-pro .cs-band::after {
  content: '';
  position: absolute;
  right: -200px; bottom: -200px;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: rgba(233,0,4,.05);
  filter: blur(60px);
  pointer-events: none;
}
.cs-pro .cs-band__inner    { position: relative; z-index: 1; }
.cs-pro .cs-band__label    { font-size: 10.5px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase; color: var(--r); margin-bottom: 16px; }
.cs-pro .cs-band__title    { font-size: clamp(1.6rem, 3vw, 2.4rem); font-weight: 900; color: var(--wh); margin-bottom: 12px; }
.cs-pro .cs-band__sub      { color: rgba(255,255,255,.55); max-width: 560px; margin: 0 auto 28px; line-height: 1.75; }
.cs-pro .cs-chips          { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
.cs-pro .cs-chip           { padding: 7px 18px; border: 1px solid rgba(233,0,4,.4); border-radius: 4px; color: rgba(255,255,255,.85); background: rgba(233,0,4,.08); font-size: 0.82rem; font-weight: 600; letter-spacing: 0.5px; }

/* ── Solution timeline ─────────────────────────────────────── */
.cs-pro .cs-timeline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 56px;
}
.cs-pro .cs-step {
  display: flex;
  gap: 22px;
  align-items: flex-start;
  padding: 28px 0;
  border-bottom: 1px solid var(--bd);
  position: relative;
}
.cs-pro .cs-timeline > .cs-step:nth-last-child(-n+2) { border-bottom: none; }
.cs-pro .cs-step__num { font-size: 2.2rem; font-weight: 900; color: var(--r); line-height: 1; flex-shrink: 0; min-width: 48px; }
.cs-pro .cs-step__body h4 { font-size: 1rem; font-weight: 700; color: var(--bk); margin-bottom: 6px; }
.cs-pro .cs-step__body p  { color: var(--mu); line-height: 1.7; }

/* ── ★ DELIVERABLES + IMAGE ────────────────────────────────── */
.cs-pro .cs-deliverables {
  padding: 80px 0;
  background: var(--lt);
}
.cs-pro .cs-deliv-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}
.cs-pro .cs-deliv-img {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 32px 80px rgba(0,0,0,.18);
}
.cs-pro .cs-deliv-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  min-height: 360px;
}
.cs-pro .cs-deliv-img__accent {
  position: absolute;
  bottom: -16px; right: -16px;
  width: 80px; height: 80px;
  background: var(--r);
  border-radius: 12px;
  z-index: -1;
}
.cs-pro .cs-deliv-cards { display: flex; flex-direction: column; gap: 24px; }
.cs-pro .cs-deliv-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 26px;
  background: var(--wh);
  border-radius: 12px;
  border: 1px solid var(--bd);
  box-shadow: 0 8px 24px rgba(0,0,0,.06);
  transition: transform .25s, box-shadow .25s, border-color .25s;
}
.cs-pro .cs-deliv-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(233,0,4,.1);
  border-color: var(--r);
}
.cs-pro .cs-deliv-card__icon {
  width: 44px; height: 44px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px;
  color: var(--wh);
  font-size: 1.1rem;
  flex-shrink: 0;
}
.cs-pro .cs-deliv-card h4 { font-size: 1rem; font-weight: 700; color: var(--bk); }
.cs-pro .cs-deliv-card p  { color: var(--mu); line-height: 1.65; }

/* ── Conclusion ────────────────────────────────────────────── */
.cs-pro .cs-conclusion {
  padding: 80px 24px;
  background: var(--bk);
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cs-pro .cs-conclusion__quote {
  font-size: 9rem;
  line-height: 0.6;
  color: rgba(233,0,4,.15);
  font-family: Georgia, serif;
  position: absolute;
  top: 30px; left: 50%;
  transform: translateX(-50%);
  pointer-events: none;
  user-select: none;
}
.cs-pro .cs-conclusion__inner  { position: relative; z-index: 1; }
.cs-pro .cs-conclusion__icon {
  width: 56px; height: 56px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 24px;
  border-radius: 50%;
  background: var(--r);
  color: var(--wh);
  font-size: 1.4rem;
}
.cs-pro .cs-conclusion__title {
  font-size: clamp(1.6rem, 3.5vw, 2.4rem);
  font-weight: 900;
  color: var(--wh);
  margin-bottom: 20px;
  letter-spacing: -0.5px;
}
.cs-pro .cs-conclusion__text {
  max-width: 680px;
  margin: 0 auto;
  color: rgba(255,255,255,.65);
  line-height: 1.85;
}

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE  — 5 breakpoints
   ═══════════════════════════════════════════════════════════════ */

/* ── Tablet landscape (≤ 1023px) ── */
@media (max-width: 1023px) {
  .cs-pro .cs-hero__card  { width: 200px; }
  .cs-pro .cs-hero        { padding: 90px 24px 80px; }
  .cs-pro .cs-section     { padding: 64px 0; }
  .cs-pro .cs-conclusion  { padding: 64px 24px; }
  .cs-pro .cs-deliverables { padding: 64px 0; }
  .cs-pro .cs-metrics-section { padding: 64px 0; }
}

/* ── Tablet portrait (≤ 860px) ── */
@media (max-width: 860px) {
  .cs-pro .cs-hero__inner { grid-template-columns: 1fr; gap: 32px; }
  .cs-pro .cs-hero__card  {
    display: grid;
    grid-template-columns: 1fr 1fr;
    width: 100%;
    max-width: 480px;
    gap: 0;
    border-radius: 10px;
  }
  .cs-pro .cs-hero__card-row                    { border-bottom: 1px solid rgba(255,255,255,.08); border-right: 1px solid rgba(255,255,255,.08); }
  .cs-pro .cs-hero__card-row:nth-child(2n)      { border-right: none; }
  .cs-pro .cs-hero__card-row:nth-last-child(-n+2) { border-bottom: none; }

  .cs-pro .cs-split        { grid-template-columns: 1fr; gap: 28px; }
  .cs-pro .cs-timeline     { grid-template-columns: 1fr; }
  .cs-pro .cs-timeline > .cs-step               { border-bottom: 1px solid var(--bd); }
  .cs-pro .cs-timeline > .cs-step:last-child    { border-bottom: none; }
  .cs-pro .cs-overview     { grid-template-columns: 1fr; gap: 8px; }
  .cs-pro .cs-section__num { font-size: 3rem; }

  /* metrics: stack image above grid */
  .cs-pro .cs-metrics-wrap { grid-template-columns: 1fr; }
  .cs-pro .cs-metrics-img  { min-height: 240px; }

  /* deliverables: stack image above cards */
  .cs-pro .cs-deliv-wrap   { grid-template-columns: 1fr; gap: 36px; }
  .cs-pro .cs-deliv-img img { min-height: 280px; }

  /* image banner: disable fixed attachment (perf on mobile) */
  .cs-pro .cs-imgbanner { background-attachment: scroll; min-height: 320px; }
}

/* ── Large phone (≤ 640px) ── */
@media (max-width: 640px) {
  .cs-pro .cs-hero        { padding: 64px 20px 56px; }
  .cs-pro .cs-section     { padding: 52px 0; }
  .cs-pro .cs-band        { padding: 56px 20px; }
  .cs-pro .cs-conclusion  { padding: 56px 20px; }
  .cs-pro .cs-inner       { padding: 0 20px; }
  .cs-pro .cs-deliverables { padding: 52px 0; }
  .cs-pro .cs-metrics-section { padding: 52px 0; }

  .cs-pro .cs-section__num  { font-size: 2.4rem; }
  .cs-pro .cs-section__head { gap: 14px; margin-bottom: 36px; }
  .cs-pro .cs-step__num     { font-size: 1.8rem; min-width: 38px; }

  .cs-pro .cs-hero__card { grid-template-columns: 1fr; max-width: 100%; }
  .cs-pro .cs-hero__card-row                      { border-right: none; }
  .cs-pro .cs-hero__card-row:nth-last-child(-n+2) { border-bottom: 1px solid rgba(255,255,255,.08); }
  .cs-pro .cs-hero__card-row:last-child           { border-bottom: none; }

  .cs-pro .cs-chips  { gap: 8px; }
  .cs-pro .cs-chip   { font-size: 0.78rem; padding: 6px 14px; }

  .cs-pro .cs-conclusion__quote { font-size: 6rem; }

  /* metrics: single column grid */
  .cs-pro .cs-metrics-grid { grid-template-columns: 1fr 1fr; }

  /* imgbanner quote */
  .cs-pro .cs-imgbanner__quote { font-size: clamp(1.1rem, 4vw, 1.5rem); padding-left: 18px; }
  .cs-pro .cs-imgbanner__content { padding: 56px 20px; }
  .cs-pro .cs-imgbanner { min-height: 280px; }
}

/* ── Standard phone (≤ 480px) ── */
@media (max-width: 480px) {
  .cs-pro .cs-hero        { padding: 56px 16px 48px; }
  .cs-pro .cs-section     { padding: 44px 0; }
  .cs-pro .cs-band        { padding: 48px 16px; }
  .cs-pro .cs-conclusion  { padding: 48px 16px; }
  .cs-pro .cs-inner       { padding: 0 16px; }
  .cs-pro .cs-metrics-section { padding: 44px 0; }
  .cs-pro .cs-deliverables    { padding: 44px 0; }

  .cs-pro .cs-hero__title  { letter-spacing: -0.5px; }
  .cs-pro .cs-hero__badge  { font-size: 9px; letter-spacing: 2px; padding: 5px 12px; }
  .cs-pro .cs-section__num { display: none; }
  .cs-pro .cs-section__head { gap: 0; margin-bottom: 28px; }

  .cs-pro .cs-chal-item { gap: 14px; padding: 16px 0; }
  .cs-pro .cs-chal-dot  { width: 8px; height: 8px; margin-top: 5px; }

  .cs-pro .cs-step { gap: 16px; padding: 22px 0; }
  .cs-pro .cs-step__num { font-size: 1.5rem; min-width: 30px; }

  .cs-pro .cs-conclusion__icon  { width: 48px; height: 48px; font-size: 1.2rem; }
  .cs-pro .cs-conclusion__quote { top: 16px; font-size: 5rem; }

  /* metrics: full-width single col */
  .cs-pro .cs-metrics-grid { grid-template-columns: 1fr; background: none; gap: 2px; }
  .cs-pro .cs-metric-box   { padding: 28px 20px; }

  .cs-pro .cs-deliv-card   { padding: 20px; }
  .cs-pro .cs-imgbanner    { min-height: 240px; }
  .cs-pro .cs-imgbanner__content { padding: 40px 16px; }
}

/* ── Small phone (≤ 360px) ── */
@media (max-width: 360px) {
  .cs-pro .cs-hero        { padding: 48px 14px 40px; }
  .cs-pro .cs-section     { padding: 36px 0; }
  .cs-pro .cs-inner       { padding: 0 14px; }
  .cs-pro .cs-band        { padding: 40px 14px; }
  .cs-pro .cs-conclusion  { padding: 40px 14px; }
  .cs-pro .cs-metrics-section { padding: 36px 0; }
  .cs-pro .cs-deliverables    { padding: 36px 0; }

  .cs-pro .cs-hero__card {
    display: flex; flex-direction: column; gap: 0;
    border: none; background: none; backdrop-filter: none; padding: 0;
  }
  .cs-pro .cs-hero__card-row  { border: none; border-bottom: 1px solid rgba(255,255,255,.07); padding: 10px 0; }
  .cs-pro .cs-hero__card-icon { width: 30px; height: 30px; font-size: 0.75rem; }
  .cs-pro .cs-hero__card-value { font-size: 0.82rem; }

  .cs-pro .cs-chip              { font-size: 0.72rem; padding: 5px 10px; }
  .cs-pro .cs-imgbanner__quote  { font-size: 1rem; }
}
</style>"""


# ─── HTML builder ─────────────────────────────────────────────────────────────
def build_page(cs, status_label):
    customer  = cs['customer']
    developer = cs['developer']
    platform  = cs['platform']
    story     = cs['story']
    problem   = cs['problem']
    solution  = cs['solution']

    parts = [p.strip() for p in re.split(r'[,/\n]', platform) if p.strip()]
    platform_short = ', '.join(parts)
    if len(platform_short) > 55:
        platform_short = ', '.join(parts[:3]) + '…'

    icon           = platform_icon(platform)
    imgs           = pick_imgs(platform)
    hero_sub       = derive_hero_sub(problem)
    banner_quote   = derive_banner_quote(problem, solution)
    challenge_html = make_challenge_html(problem)
    solution_html  = make_solution_html(solution)
    story_block    = make_story_block(story)
    tech_chips     = make_tech_chips(platform)
    metrics        = derive_metrics(problem, solution, platform)
    deliverables   = make_deliverables(solution)
    conclusion     = derive_conclusion(customer, platform_short, solution)

    # Metric boxes HTML
    metric_boxes = '\n'.join(f'''<div class="cs-metric-box">
  <i class="cs-metric-box__icon {m["icon"]}"></i>
  <span class="cs-metric-box__num">{m["num"]}</span>
  <span class="cs-metric-box__label">{m["label"]}</span>
</div>''' for m in metrics)

    return f"""\
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
  1. Add to Appearance › Theme Options › Custom Head Code (if FA not loaded):
       <link rel="stylesheet"
             href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  2. Add a Custom HTML block to the page.
  3. Paste ONLY the block between WORDPRESS PASTE START / END.
-->

<!-- === WORDPRESS PASTE START === -->
{CSS}

<section class="cs-pro">

  <!-- ═══ HERO ═══ -->
  <div class="cs-hero">
    <div class="cs-hero__inner">
      <div>
        <span class="cs-hero__badge">
          <i class="{icon}"></i> Case Study
        </span>
        <h1 class="cs-hero__title"><span>{customer}</span></h1>
        <p class="cs-hero__sub">{hero_sub}</p>
      </div>
      <div class="cs-hero__card">
        <div class="cs-hero__card-row">
          <div class="cs-hero__card-icon"><i class="fa-solid fa-building"></i></div>
          <div>
            <div class="cs-hero__card-label">Client</div>
            <div class="cs-hero__card-value">{customer}</div>
          </div>
        </div>
        <div class="cs-hero__card-row">
          <div class="cs-hero__card-icon"><i class="fa-solid fa-user-tie"></i></div>
          <div>
            <div class="cs-hero__card-label">Developer</div>
            <div class="cs-hero__card-value">{developer}</div>
          </div>
        </div>
        <div class="cs-hero__card-row">
          <div class="cs-hero__card-icon"><i class="{icon}"></i></div>
          <div>
            <div class="cs-hero__card-label">Platform</div>
            <div class="cs-hero__card-value">{platform_short}</div>
          </div>
        </div>
        <div class="cs-hero__card-row">
          <div class="cs-hero__card-icon"><i class="fa-solid fa-circle-check"></i></div>
          <div>
            <div class="cs-hero__card-label">Status</div>
            <div class="cs-hero__card-value">{status_label}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ═══ OVERVIEW ═══ -->
  {story_block}

  <!-- ═══ CHALLENGE ═══ -->
  <div class="cs-section cs-section--alt">
    <div class="cs-inner">
      <div class="cs-section__head">
        <div class="cs-section__num">01</div>
        <div>
          <div class="cs-eyebrow">The Problem</div>
          <h2 class="cs-section__title">The Challenge</h2>
          <div class="cs-section__rule"></div>
        </div>
      </div>
      {challenge_html}
    </div>
  </div>

  <!-- ═══ ★ IMAGE BANNER ═══ -->
  <div class="cs-imgbanner"
       style="background-image:url('{img_url(imgs['banner'])}')">
    <div class="cs-imgbanner__overlay"></div>
    <div class="cs-imgbanner__content">
      <div class="cs-imgbanner__label">Key Insight</div>
      <p class="cs-imgbanner__quote">{banner_quote}</p>
    </div>
  </div>

  <!-- ═══ ★ METRICS ROW ═══ -->
  <div class="cs-metrics-section">
    <div class="cs-metrics-wrap">
      <div class="cs-metrics-img"
           style="background-image:url('{img_url(imgs['metrics'])}')">
      </div>
      <div class="cs-metrics-grid">
        {metric_boxes}
      </div>
    </div>
  </div>

  <!-- ═══ PLATFORM BAND ═══ -->
  <div class="cs-band">
    <div class="cs-band__inner">
      <div class="cs-band__label">Technology Stack</div>
      <h3 class="cs-band__title">Built on Modern Infrastructure</h3>
      <p class="cs-band__sub">
        Powered by {platform_short} — engineered for reliability and scale.
      </p>
      <div class="cs-chips">{tech_chips}</div>
    </div>
  </div>

  <!-- ═══ SOLUTION ═══ -->
  <div class="cs-section">
    <div class="cs-inner">
      <div class="cs-section__head">
        <div class="cs-section__num">02</div>
        <div>
          <div class="cs-eyebrow">Our Approach</div>
          <h2 class="cs-section__title">The Solution</h2>
          <div class="cs-section__rule"></div>
        </div>
      </div>
      <div class="cs-timeline">
        {solution_html}
      </div>
    </div>
  </div>

  <!-- ═══ ★ DELIVERABLES + IMAGE ═══ -->
  <div class="cs-deliverables">
    <div class="cs-inner">
      <div class="cs-section__head">
        <div class="cs-section__num">03</div>
        <div>
          <div class="cs-eyebrow">What We Built</div>
          <h2 class="cs-section__title">Key Deliverables</h2>
          <div class="cs-section__rule"></div>
        </div>
      </div>
      <div class="cs-deliv-wrap">
        <div class="cs-deliv-img">
          <img src="{img_url(imgs['process'], w=900)}"
               alt="Project process visual" loading="lazy"/>
          <div class="cs-deliv-img__accent"></div>
        </div>
        <div class="cs-deliv-cards">
          {deliverables}
        </div>
      </div>
    </div>
  </div>

  <!-- ═══ CONCLUSION ═══ -->
  <div class="cs-conclusion">
    <div class="cs-conclusion__quote">&ldquo;</div>
    <div class="cs-conclusion__inner">
      <div class="cs-conclusion__icon">
        <i class="fa-solid fa-trophy"></i>
      </div>
      <h2 class="cs-conclusion__title">The Outcome</h2>
      <p class="cs-conclusion__text">{conclusion}</p>
    </div>
  </div>

</section>
<!-- === WORDPRESS PASTE END === -->

</html>"""


# ─── Run ─────────────────────────────────────────────────────────────────────
with open(CSV_FILE, encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader); next(reader)
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
    if cs['rating'] in ('review', 'publish'):
        label    = 'Completed'
        suffix   = 'publish'   if cs['rating'] == 'publish' else 'review'
        filename = f"case-study-{cs['id']}-{suffix}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(build_page(cs, label))
        print(f"  {filename}  —  {cs['customer']}")

print("Done.")
