"""
Rebuild blog/index.html and sitemap.xml from all blog posts in the blog/ directory.
Run after adding new posts: python build_blog_index.py
"""
import os, re, json
from datetime import datetime

BLOG_DIR  = os.path.join(os.path.dirname(__file__), 'blog')
SITE_URL  = 'https://splashlens.com'
TODAY     = datetime.now().strftime('%Y-%m-%d')

def extract_meta(html, field):
    patterns = {
        'title':       r'<title>(.*?)</title>',
        'description': r'<meta name="description" content="(.*?)"',
        'og:title':    r'<meta property="og:title" content="(.*?)"',
        'og:image':    r'<meta property="og:image" content="(.*?)"',
        'date':        r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})"',
        'category':    r'<meta property="article:section" content="(.*?)"',
        'faq':         r'"@type"\s*:\s*"FAQPage"',
    }
    m = re.search(patterns[field], html, re.DOTALL)
    return m.group(1) if m else ''

posts = []
for fname in sorted(os.listdir(BLOG_DIR)):
    if fname == 'index.html' or not fname.endswith('.html'):
        continue
    path = os.path.join(BLOG_DIR, fname)
    html = open(path, encoding='utf-8').read()
    title = extract_meta(html, 'og:title') or extract_meta(html, 'title')
    title = title.replace(' | PoolLens', '').strip()
    desc  = extract_meta(html, 'description')
    img   = extract_meta(html, 'og:image')
    date  = extract_meta(html, 'date') or TODAY
    has_faq = bool(re.search(r'"@type"\s*:\s*"FAQPage"', html))

    # Infer category from filename/title keywords
    def cat(t, f):
        t, f = t.lower(), f.lower()
        if any(x in f for x in ['e01','e04','e05','error','err','lo-error','lockout','red-light']): return 'Error Codes'
        if any(x in f for x in ['algae','slam','shock','green','turning']): return 'Water Chemistry'
        if any(x in t for x in ['ph','chlorine','chemical','alkalinity','calcium','cya','salt','sanitiz','baquacil']): return 'Water Chemistry'
        if any(x in f for x in ['filter','pump','heater','robot','cleaner','salt-cell','automation','plumbing','motor']): return 'Equipment'
        if any(x in f for x in ['winter','open','close','season','spring','fall']): return 'Seasonal'
        if any(x in f for x in ['business','pricing','customer','insurance','route','software','certif','upsell']): return 'Pool Pro'
        if any(x in f for x in ['best-','guide','review','how-to','how-long','what-is','why-']): return 'Guides'
        return 'Pool Care'

    posts.append({
        'url':     f'{SITE_URL}/blog/{fname}',
        'file':    fname,
        'title':   title,
        'desc':    desc,
        'img':     img or 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=400&fit=crop',
        'date':    date,
        'faq':     has_faq,
        'cat':     cat(title, fname),
    })

posts.sort(key=lambda p: p['date'], reverse=True)

# ── Blog categories ──────────────────────────────────────────────
cats = sorted(set(p['cat'] for p in posts))

cat_pills = ' '.join([
    f'<button class="cat-pill active" data-cat="all" onclick="filterCat(\'all\',this)">All ({len(posts)})</button>',
] + [
    f'<button class="cat-pill" data-cat="{c}" onclick="filterCat(\'{c}\',this)">{c} ({sum(1 for p in posts if p["cat"]==c)})</button>'
    for c in cats
])

# ── Post cards HTML ────────────────────────────────────────────
def card(p):
    faq_badge = '<span style="background:#e0f2fe;color:#0369a1;padding:1px 7px;border-radius:100px;font-size:10px;font-weight:700;margin-left:6px;">FAQ</span>' if p['faq'] else ''
    return f'''<article class="post-card" data-cat="{p['cat']}">
  <a href="/blog/{p['file']}" style="text-decoration:none;">
    <img src="{p['img']}" alt="{p['title']}" loading="lazy"
      style="width:100%;height:160px;object-fit:cover;border-radius:12px 12px 0 0;display:block;"
      onerror="this.src='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=400&fit=crop'">
    <div style="padding:14px;">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap;">
        <span style="background:#f0f9ff;color:#0284c7;padding:2px 8px;border-radius:100px;font-size:10px;font-weight:700;">{p['cat']}</span>
        {faq_badge}
        <span style="margin-left:auto;color:#94a3b8;font-size:10px;">{p['date']}</span>
      </div>
      <h2 style="font-size:15px;font-weight:800;color:#0f172a;line-height:1.35;margin-bottom:6px;">{p['title']}</h2>
      <p style="font-size:12px;color:#64748b;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">{p['desc']}</p>
    </div>
  </a>
</article>'''

cards_html = '\n'.join(card(p) for p in posts)

# ── index.html ────────────────────────────────────────────────
index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pool Service Blog — Error Codes, Chemistry & Pro Tips | SplashLens</title>
<meta name="description" content="Pool tech guides, error code fixes, water chemistry tutorials, seasonal maintenance checklists, and pool pro business tips. Free field reference from SplashLens.">
<link rel="canonical" href="{SITE_URL}/blog/">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/blog/">
<meta property="og:title" content="Pool Service Blog — Error Codes, Chemistry & Pro Tips | SplashLens">
<meta property="og:description" content="Pool tech guides, error code fixes, water chemistry tutorials, and pool pro business tips. Free from SplashLens.">
<meta property="og:image" content="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=630&fit=crop">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Blog","name":"SplashLens Blog","url":"{SITE_URL}/blog/","description":"Pool service guides, error codes, chemistry tutorials, and pro tips.","publisher":{{"@type":"Organization","name":"SplashLens","url":"{SITE_URL}"}}}}
</script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:#f8fafc;color:#0f172a}}
nav{{background:#0369a1;padding:0 24px;height:56px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10}}
.nav-logo{{color:white;font-weight:800;font-size:1.1rem;text-decoration:none}}
.nav-cta{{background:white;color:#0369a1;padding:7px 18px;border-radius:100px;font-weight:700;font-size:.85rem;text-decoration:none}}
.hero{{background:linear-gradient(135deg,#0369a1,#0284c7);color:white;text-align:center;padding:48px 24px 40px}}
.hero h1{{font-size:clamp(1.4rem,4vw,2rem);font-weight:900;margin-bottom:10px}}
.hero p{{font-size:1rem;opacity:.85;max-width:560px;margin:0 auto 20px}}
.search-wrap{{max-width:480px;margin:0 auto;position:relative}}
.search-wrap input{{width:100%;padding:13px 18px;border-radius:100px;border:none;font-size:15px;outline:none;color:#0f172a}}
.cat-bar{{display:flex;gap:8px;overflow-x:auto;padding:16px 16px 8px;scrollbar-width:none;-webkit-overflow-scrolling:touch}}
.cat-bar::-webkit-scrollbar{{display:none}}
.cat-pill{{padding:6px 14px;border-radius:100px;border:1px solid #e2e8f0;background:white;color:#64748b;font-size:12px;font-weight:700;cursor:pointer;white-space:nowrap;transition:.15s}}
.cat-pill.active{{background:#0284c7;border-color:#0284c7;color:white}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;padding:0 16px 80px;max-width:1200px;margin:0 auto}}
.post-card{{background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06);transition:.2s}}
.post-card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.1)}}
.post-card a{{color:inherit}}
.hidden{{display:none!important}}
.no-results{{grid-column:1/-1;text-align:center;padding:48px;color:#64748b;font-size:14px}}
footer{{background:#0f172a;color:#64748b;text-align:center;padding:32px 24px;font-size:13px}}
footer a{{color:#38bdf8;text-decoration:none}}
@media(max-width:480px){{.hero h1{{font-size:1.3rem}}.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">SplashLens</a>
  <a href="https://app.splashlens.com" class="nav-cta" target="_blank" rel="noopener">Open App →</a>
</nav>

<div class="hero">
  <h1>Pool Service Knowledge Base</h1>
  <p>Error code fixes, water chemistry guides, equipment how-tos, and pool pro business tips — all free.</p>
  <div class="search-wrap">
    <input type="search" placeholder="Search {len(posts)} articles…" oninput="searchPosts(this.value)" id="search-input">
  </div>
</div>

<div class="cat-bar" id="cat-bar">
  {cat_pills}
</div>

<div class="grid" id="post-grid">
  {cards_html}
</div>

<div class="no-results" id="no-results" style="display:none;">No articles match your search.</div>

<footer>
  <p style="margin-bottom:8px;color:#94a3b8;">© 2026 SplashLens · Free forever for pool professionals</p>
  <p><a href="/">Home</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="https://app.splashlens.com" target="_blank" rel="noopener">Open App</a></p>
</footer>

<script>
let _activeCat = 'all';
let _query     = '';

function filterCat(cat, btn) {{
  _activeCat = cat;
  document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  applyFilters();
}}

function searchPosts(q) {{
  _query = q.toLowerCase().trim();
  applyFilters();
}}

function applyFilters() {{
  const cards = document.querySelectorAll('.post-card');
  let shown = 0;
  cards.forEach(card => {{
    const catMatch = _activeCat === 'all' || card.dataset.cat === _activeCat;
    const title    = card.querySelector('h2')?.textContent.toLowerCase() || '';
    const desc     = card.querySelector('p')?.textContent.toLowerCase() || '';
    const qMatch   = !_query || title.includes(_query) || desc.includes(_query);
    const show     = catMatch && qMatch;
    card.classList.toggle('hidden', !show);
    if (show) shown++;
  }});
  document.getElementById('no-results').style.display = shown ? 'none' : 'block';
}}
</script>
</body>
</html>'''

# Write blog index
with open(os.path.join(BLOG_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print(f'Blog index written: {len(posts)} posts')

# ── sitemap.xml ────────────────────────────────────────────────
sitemap_urls = [
    f'  <url><loc>{SITE_URL}/</loc><changefreq>weekly</changefreq><priority>1.0</priority><lastmod>{TODAY}</lastmod></url>',
    f'  <url><loc>{SITE_URL}/blog/</loc><changefreq>daily</changefreq><priority>0.9</priority><lastmod>{TODAY}</lastmod></url>',
    f'  <url><loc>{SITE_URL}/privacy.html</loc><changefreq>yearly</changefreq><priority>0.2</priority></url>',
    f'  <url><loc>{SITE_URL}/terms.html</loc><changefreq>yearly</changefreq><priority>0.2</priority></url>',
]
for p in posts:
    sitemap_urls.append(f'  <url><loc>{p["url"]}</loc><changefreq>monthly</changefreq><priority>0.7</priority><lastmod>{p["date"]}</lastmod></url>')

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap += '\n'.join(sitemap_urls)
sitemap += '\n</urlset>'

with open(os.path.join(os.path.dirname(__file__), 'sitemap.xml'), 'w', encoding='utf-8') as f:
    f.write(sitemap)
print(f'Sitemap written: {len(sitemap_urls)} URLs')
print('Done.')
