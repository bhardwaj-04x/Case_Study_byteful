import csv
import os
from pathlib import Path

# Read the CSV file
csv_file = Path(r'c:\Users\prana\OneDrive\Desktop\CaseStudyByteful\case-study-input-sheet.csv')

case_studies = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)  # Skip header row

    for row in reader:
        if len(row) >= 9:  # Ensure we have enough columns
            case_study = {
                'id': row[0].strip(),
                'rating': row[1].strip(),
                'comments': row[2].strip(),
                'story': row[3].strip(),
                'problem': row[4].strip(),
                'solution': row[5].strip(),
                'developer': row[6].strip(),
                'customer': row[7].strip(),
                'platform': row[8].strip()
            }
            case_studies.append(case_study)

print(f"Found {len(case_studies)} case studies")

# Filter for Review and Publish
review_studies = [cs for cs in case_studies if cs['rating'].lower() == 'review']
publish_studies = [cs for cs in case_studies if cs['rating'].lower() == 'publish']

print(f"Review studies: {len(review_studies)}")
print(f"Publish studies: {len(publish_studies)}")

# Template for HTML generation
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
</head>
<style>
/* =========================
   DEFAULT (mobile first)
========================= */
.d-none {{
  display: none !important;
}}

.d-block {{
  display: block !important;
}}

/* =========================
   MD BREAKPOINT (≥768px)
========================= */
@media (min-width: 768px) {{
  .d-md-none {{
    display: none !important;
  }}

  .d-md-block {{
    display: block !important;
  }}
}}

/* =========================
   OPTIONAL: reverse behavior for mobile
========================= */
@media (max-width: 767px) {{
  .d-md-none {{
    display: block !important;
  }}

  .d-md-block {{
    display: none !important;
  }}
}}
:root{{
  --primary:#E90004;
  --black:#0b0b0b;
  --dark:#1a1a1a;
  --text:#111;
  --muted:#666;
  --light:#f6f7fb;
  --border:#eaeaea;
}}

body {{
  margin:0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text);
  background:#f5f7fb;
  line-height:1.6;
}}

p,
ul {{
  margin:0;
}}

ul {{
  padding:0;
}}

.cs-pro {{
  width:100%;
}}

/* =========================
   HERO
========================= */

.cs-hero{{
  position:relative;
  min-height:520px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  text-align:center;
  padding:100px 20px;
  background:linear-gradient(135deg,var(--black),var(--dark));
  overflow:hidden;
}}

.cs-hero::before{{
  content:'';
  position:absolute;
  inset:0;
  background:url('https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1600&q=80') center/cover no-repeat;
  opacity:0.12;
}}

.cs-hero h1{{
  position:relative;
  font-size:clamp(1.8rem,4vw,3.2rem);
  font-weight:900;
  color:#fff;
  max-width:900px;
  line-height:1.2;
}}

.cs-hero p{{
  position:relative;
  margin-top:14px;
  font-size:clamp(0.95rem,2vw,1.1rem);
  color:rgba(255,255,255,0.8);
}}

/* badge */
.cs-hero-badge{{
  position:relative;
  margin-bottom:18px;
  padding:6px 16px;
  border-radius:50px;
  border:1px solid var(--primary);
  color:var(--primary);
  background:rgba(233,0,4,0.08);
  font-size:12px;
  letter-spacing:2px;
  text-transform:uppercase;
}}

/* =========================
   INFO BAR
========================= */

.cs-infobar{{
  display:flex;
  flex-wrap:wrap;
  justify-content:center;
  gap:14px;
  padding:18px 12px;
  background:#fff;
  border-bottom:1px solid var(--border);
}}

.cs-infobar-item{{
  display:flex;
  align-items:center;
  gap:10px;
  padding:10px 14px;
  border-radius:12px;
  border:1px solid var(--border);
  background:#fff;
  box-shadow:0 6px 20px rgba(0,0,0,0.04);
  transition:0.3s;
}}

.cs-infobar-item:hover{{
  transform:translateY(-2px);
  border-color:var(--primary);
}}

.cs-infobar-item i{{
  width:38px;
  height:38px;
  display:flex;
  align-items:center;
  justify-content:center;
  background:rgba(233,0,4,0.1);
  color:var(--primary);
  border-radius:10px;
}}

.cs-infobar{{
  padding:18px 20px;
}}

.cs-infobar-item{{
  flex:1 1 240px;
  min-width:240px;
  justify-content:flex-start;
}}

.cs-infobar-item div{{
  line-height:1.35;
}}

.cs-infobar-item strong{{
  display:block;
  font-size:0.95rem;
  font-weight:700;
}}

.cs-section h2{{
  margin-top:0;
}}

.cs-visual{{
  padding:60px 0;
}}

.cs-visual-content{{
  color:#fff;
  text-align:center;
}}

/* =========================
   INTRO
========================= */

.cs-intro{{
  width:100%;
  padding:80px 20px;
  background:#fff;
}}

.cs-intro .section-inner{{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:24px;
  max-width:1200px;
  margin:auto;
  padding:0 20px;
}}

.cs-intro > div{{
  background:#fff;
  padding:24px;
  border-radius:12px;
  border:1px solid var(--border);
  border-left:4px solid var(--primary);
  box-shadow:0 10px 30px rgba(0,0,0,0.04);
}}

.cs-intro p{{
  color:var(--muted);
  line-height:1.8;
}}

/* =========================
   SECTION BASE
========================= */

.cs-section{{
  width:100%;
  padding:80px 20px;
  background:#fff;
}}

.cs-section.alt{{
  width:100%;
  background:#f8f9fc;
  padding:80px 20px;
}}

.section-inner{{
  max-width:1200px;
  margin:auto;
  padding:0 20px;
}}

.cs-section h2{{
  font-size:clamp(1.4rem,3vw,2rem);
  font-weight:900;
  margin-bottom:20px;
}}

.cs-section h2::after{{
  content:'';
  width:60px;
  height:4px;
  background:var(--primary);
  display:block;
  margin-top:10px;
  border-radius:2px;
}}

.cs-section > p{{
  color:var(--muted);
  line-height:1.8;
  max-width:750px;
}}

/* =========================
   PROBLEM LIST
========================= */

.cs-problem-list{{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:16px;
  margin-top:30px;
}}

.cs-problem-list li{{
  list-style:none;
  display:flex;
  gap:12px;
  padding:18px;
  border-radius:12px;
  background:#fff;
  border:1px solid var(--border);
  box-shadow:0 6px 20px rgba(0,0,0,0.04);
  transition:0.3s;
}}

.cs-problem-list li:hover{{
  transform:translateY(-4px);
  border-color:var(--primary);
}}

/* =========================
   CARDS (SOLUTION)
========================= */

.cs-cards{{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:18px;
  margin-top:30px;
}}

.cs-cards .card{{
  background:#fff;
  border-radius:14px;
  padding:26px;
  text-align:center;
  border:1px solid var(--border);
  box-shadow:0 8px 25px rgba(0,0,0,0.05);
  transition:0.3s;
}}

.cs-cards .card:hover{{
  transform:translateY(-8px);
  border-color:var(--primary);
  box-shadow:0 18px 50px rgba(233,0,4,0.18);
}}

.cs-cards .card i{{
  width:60px;
  height:60px;
  display:flex;
  align-items:center;
  justify-content:center;
  margin:0 auto 14px;
  border-radius:14px;
  background:linear-gradient(135deg,var(--primary),var(--black));
  color:#fff;
  font-size:1.3rem;
}}

/* =========================
   FLOW
========================= */

.cs-flow{{
  display:flex;
  flex-wrap:wrap;
  justify-content:center;
  align-items:center;
  gap:12px;
  margin-top:30px;
}}

.fa{{
  font-size:1.3rem !important;
}}

.cs-flow-step{{
  font-size: 1rem;
  width:150px;
  height: 137px;
  text-align:center;
  padding:14px;
  border-radius:14px;
  background:#fff;
}}

.step-icon{{
  width:60px;
  height:60px;
  margin:0 auto 10px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  background:linear-gradient(135deg,var(--primary),var(--black));
  color:#fff;
}}

.cs-flow-arrow{{
  color:var(--primary);
}}

/* =========================
   COUNTERS
========================= */

.cs-counters{{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:18px;
  margin-top:30px;
}}

.cs-counter-box{{
  background:linear-gradient(135deg,var(--black),var(--dark));
  color:#fff;
  border-radius:16px;
  padding:30px 18px;
  text-align:center;
  box-shadow:0 20px 60px rgba(233,0,4,0.15);
  transition:0.3s;
}}

.cs-counter-box:hover{{
  transform:translateY(-6px);
}}

.counter-num{{
  font-size:2.6rem;
  font-weight:900;
}}

/* =========================
   PROGRESS
========================= */

.cs-progress-wrap{{
  margin-top:40px;
}}

.progress-box{{
  margin-bottom:20px;
}}

.progress-box > span{{
  display:flex;
  justify-content:space-between;
  font-weight:600;
}}

.bar{{
  height:10px;
  background:#eee;
  border-radius:50px;
  overflow:hidden;
}}

.bar > div{{
  height:100%;
  width:0;
  background:linear-gradient(90deg,var(--primary),var(--black));
  transition:1.2s ease;
}}

/* =========================
   VISUAL SECTION
========================= */

.cs-visual{{
  width:100%;
  height:300px;
  display:flex;
  align-items:center;
  justify-content:center;
  text-align:center;
  position:relative;
  background:linear-gradient(135deg,var(--black),var(--dark));
}}

.cs-visual::before{{
  content:'';
  position:absolute;
  inset:0;
  background:url('https://images.unsplash.com/photo-1518770660439-4636190af475?w=1600&q=80') center/cover no-repeat;
  opacity:0.15;
}}

.cs-conclusion{{
  width:100%;
  padding:80px 20px;
  background:#fff;
  text-align:center;
}}

.big-icon{{
  font-size:3rem !important;
  color:var(--primary);
  margin-bottom:16px;
}}

.cs-visual-content h3{{
  color:var(--primary);
}}

.cs-visual-content p{{
  color:white;
}}

/* =========================
   RESPONSIVE
========================= */

@media (max-width:768px){{
  .fa{{
    font-size: 0.8rem !important;
  }}

  .cs-intro{{
    grid-template-columns:1fr;
    padding:40px 16px;
  }}

  .cs-hero{{
    min-height:420px;
    padding:80px 16px;
  }}

  .cs-flow{{
    flex-direction:column;
  }}

  .cs-section{{
    padding:40px 16px;
  }}

  .cs-conclusion{{
    padding:40px 16px;
  }}

  .cs-infobar{{
    flex-wrap:nowrap;
    overflow-x:auto;
    justify-content:flex-start;
  }}
}}
</style>
<body>
<section class="cs-pro">

  <div class="cs-hero">
    <span class="cs-hero-badge"><i class="fa fa-database"></i> &nbsp; Case Study</span>
    <h1>{hero_title}</h1>
    <p>{hero_subtitle}</p>
  </div>

  <div class="cs-infobar">
    <div class="cs-infobar-item">
      <i class="fa fa-building"></i>
      <div><strong>Client</strong><br><span>{customer}</span></div>
    </div>
    <div class="cs-infobar-item">
      <i class="fa fa-user"></i>
      <div><strong>Developer</strong><br><span>{developer}</span></div>
    </div>
    <div class="cs-infobar-item">
      <i class="fa-solid fa-layer-group"></i>
      <div><strong>Tech Stack</strong><br><span>{platform}</span></div>
    </div>
    <div class="cs-infobar-item">
      <i class="fa fa-server"></i>
      <div><strong>Status</strong><br><span>{status}</span></div>
    </div>
  </div>

  <div class="cs-intro"><div class="section-inner">
    <div>
      <p>
        {intro_1}
      </p>
    </div>
    <div>
      <p>
        {intro_2}
      </p>
    </div>
  </div>
  </div>

  <div class="cs-section"><div class="section-inner">
    <h2>The Challenge</h2>
    <p>{problem}</p>
  </div>
  </div>

  <div class="cs-section alt"><div class="section-inner">
    <h2>The Solution</h2>
    <p>{solution}</p>
  </div>
  </div>

  <div class="cs-visual"><div class="section-inner">
    <div class="cs-visual-content">
      <h3><i class="fa fa-circle-nodes"></i> &nbsp; Built on Modern Architecture</h3>
      <p>Powered by {platform} — engineered for reliability and scale.</p>
    </div>
  </div>
  </div>

  <div class="cs-conclusion"><div class="section-inner">
    <i class="fa fa-rocket big-icon"></i>
    <h2>Conclusion</h2>
    <p>
      {conclusion}
    </p>
  </div>
  </div>

</section>

</body>
</html>'''

def generate_html(case_study, status):
    """Generate HTML for a case study"""
    title = f"Case Study {case_study['id']} - {case_study['customer']}"

    # Extract key information for hero
    hero_title = f"Transforming {case_study['customer']} with {case_study['platform']}"
    hero_subtitle = f"Success story with {case_study['developer']}"

    # Split problem/solution into intro sections
    problem_parts = case_study['problem'].split('\n\n')[:2]
    intro_1 = problem_parts[0] if len(problem_parts) > 0 else case_study['problem'][:300] + "..."
    intro_2 = problem_parts[1] if len(problem_parts) > 1 else "Our solution delivered exceptional results."

    # Conclusion
    conclusion = f"This solution transformed {case_study['customer']}'s operations. By implementing {case_study['platform']}, we achieved significant improvements in efficiency and scalability."

    html = html_template.format(
        title=title,
        hero_title=hero_title,
        hero_subtitle=hero_subtitle,
        customer=case_study['customer'],
        developer=case_study['developer'],
        platform=case_study['platform'],
        status=status,
        intro_1=intro_1,
        intro_2=intro_2,
        problem=case_study['problem'],
        solution=case_study['solution'],
        conclusion=conclusion
    )

    return html

# Generate pages for review studies
for cs in review_studies:
    if cs['id']:
        filename = f"case-study-{cs['id']}-review.html"
        html_content = generate_html(cs, "In Review")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated: {filename}")

# Generate pages for publish studies
for cs in publish_studies:
    if cs['id']:
        filename = f"case-study-{cs['id']}-publish.html"
        html_content = generate_html(cs, "Published")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated: {filename}")

print("HTML generation complete!")