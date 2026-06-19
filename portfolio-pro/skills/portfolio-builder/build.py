#!/usr/bin/env python3
"""
Portfolio Pro — deterministic renderer.
Takes a canonical resume.json + a niche template + theme/accent and emits a single
self-contained index.html. The LLM agent produces resume.json (handles messy resumes);
THIS script just stamps it out reliably. No third-party dependencies.

Usage:
  python3 build.py --resume resume.json --template data-analyst --theme light \
                   --accent "#4f46e5" --out index.html
"""
import re, html, json, sys, os, argparse
from urllib.parse import quote

# ---------------------------------------------------------------- mini-mustache
TAG = re.compile(r'\{\{(\{)?\s*([#^/&!]?)\s*([\w.]*)\s*\}?\}\}')

def compile_tmpl(text):
    tokens, pos = [], 0
    for m in TAG.finditer(text):
        if m.start() > pos:
            tokens.append(('text', text[pos:m.start()]))
        raw, sigil, name = bool(m.group(1)), m.group(2), m.group(3)
        if   sigil == '#': tokens.append(('section', name))
        elif sigil == '^': tokens.append(('inverted', name))
        elif sigil == '/': tokens.append(('end', name))
        elif sigil == '&' or raw: tokens.append(('raw', name))
        elif sigil == '!': pass
        else: tokens.append(('var', name))
        pos = m.end()
    if pos < len(text):
        tokens.append(('text', text[pos:]))
    root, stack = [], None
    stack = [root]
    for t in tokens:
        if t[0] in ('section', 'inverted'):
            node = [t[0], t[1], []]
            stack[-1].append(node)
            stack.append(node[2])
        elif t[0] == 'end':
            stack.pop()
        else:
            stack[-1].append(t)
    return root

def get(ctx, key):
    if key == '.':
        return ctx[-1]
    parts = key.split('.')
    for frame in reversed(ctx):
        if isinstance(frame, dict) and parts[0] in frame:
            v = frame[parts[0]]
            for p in parts[1:]:
                v = v[p] if isinstance(v, dict) and p in v else None
                if v is None: break
            return v
    return None

def render(nodes, ctx):
    out = []
    for n in nodes:
        if n[0] == 'text':
            out.append(n[1])
        elif n[0] == 'var':
            v = get(ctx, n[1]); out.append(html.escape(str(v)) if v not in (None, '') else '')
        elif n[0] == 'raw':
            v = get(ctx, n[1]); out.append(str(v) if v not in (None, '') else '')
        elif n[0] == 'section':
            v = get(ctx, n[1])
            if isinstance(v, list):
                for it in v: out.append(render(n[2], ctx + [it]))
            elif isinstance(v, dict):
                out.append(render(n[2], ctx + [v]))
            elif v:
                out.append(render(n[2], ctx + [v]))
        elif n[0] == 'inverted':
            v = get(ctx, n[1])
            if not v: out.append(render(n[2], ctx))
    return ''.join(out)

def mustache(text, data):
    return render(compile_tmpl(text), [data])

# ---------------------------------------------------------------- helpers
def ink_for(hexcolor):
    h = hexcolor.lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return '#ffffff' if lum < 150 else '#11131a'

# Strip "AI tells": em/en dashes and exotic spaces from DISPLAYED text (not URLs/emails).
SKIP_KEYS = {'url', 'link', 'photo', 'email', '_roles_json'}
def sanitize(obj, key=None):
    if isinstance(obj, dict):
        return {k: sanitize(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v, key) for v in obj]
    if isinstance(obj, str) and key not in SKIP_KEYS:
        return (obj.replace('—', '-').replace('–', '-')
                   .replace(' ', ' ').replace(' ', ' ')
                   .replace('…', '...'))
    return obj

def derive(resume):
    name = resume.get('name', '')
    resume['_initials'] = ''.join(p[0] for p in name.split()[:2]).upper() or '·'
    roles = resume.get('roles') or ([resume['headline']] if resume.get('headline') else [])
    resume['_roles_json'] = json.dumps(roles)
    links = (resume.get('contact') or {}).get('links') or []
    resume['_primary_link'] = links[0] if links else None
    keys = ['metrics', 'experience', 'projects', 'skills', 'education',
            'certifications', 'publications', 'awards', 'languages', 'testimonials', 'chatbot']
    resume['has'] = {k: bool(resume.get(k)) for k in keys}
    # credibility marquee feed (companies, headline metrics, top skills, schools)
    mq = []
    for e in resume.get('experience') or []:
        if e.get('company'): mq.append(e['company'])
    for m in resume.get('metrics') or []:
        if m.get('value') and m.get('label'): mq.append(f"{m['value']} {m['label']}")
    for s in (resume.get('skills') or [])[:2]:
        mq += (s.get('items') or [])[:3]
    for ed in resume.get('education') or []:
        if ed.get('school'): mq.append(ed['school'])
    resume['_marquee'] = mq
    resume['_chatbot_json'] = json.dumps(resume.get('chatbot') or [])
    # hero quick-facts helpers
    sk = resume.get('skills') or []
    resume['_top_tools'] = ', '.join((sk[0].get('items') or [])[:4]) if sk else ''
    # icon slug per skill group (keyword match -> inline SVG sprite id)
    ICONS = [('ai', ['ai', 'ml', 'machine', 'model', 'genai', 'llm', 'data scien']),
             ('chart', ['analyt', 'data', 'bi', 'metric', 'sql', 'query', 'forecast', 'stat']),
             ('cloud', ['cloud', 'aws', 'gcp', 'azure', 'infra', 'devops']),
             ('code', ['language', 'program', 'python', 'java', 'engineer', 'develop', 'framework']),
             ('shield', ['govern', 'security', 'compliance', 'privacy', 'risk']),
             ('users', ['leader', 'team', 'stakeholder', 'people', 'manage', 'communicat']),
             ('wrench', ['tool', 'platform', 'method', 'process', 'ops'])]
    for g in sk:
        if not g.get('icon'):
            t = (g.get('group', '') + ' ' + ' '.join(g.get('items', []))).lower()
            g['icon'] = next((slug for slug, kws in ICONS if any(k in t for k in kws)), 'spark')
    # normalize certifications to {name, issuer}
    certs = resume.get('certifications') or []
    resume['certifications'] = [c if isinstance(c, dict) else {'name': c, 'issuer': ''} for c in certs]
    # mark most recent role as current (for timeline highlight)
    exp = resume.get('experience') or []
    if exp:
        exp[0]['_current'] = True
    resume['_focus_block'] = bool(resume.get('focus'))
    for i, p in enumerate(resume.get('projects') or []):
        p['_idx'] = f"{i + 1:02d}"
        seed = (p.get('title') or str(i))
        h2 = (sum(ord(c) for c in seed) * 7) % 360
        p['_grad'] = f"linear-gradient(135deg,var(--accent),hsl({h2}deg 60% 48%))"
    for e in (resume.get('experience') or []):
        e['_logo_letter'] = (e.get('company') or '?').strip()[:1].upper()
    return resume

JS = """
(function(){
  var root=document.documentElement;
  var saved=localStorage.getItem('pp-theme'); if(saved) root.setAttribute('data-theme',saved);
  var b=document.getElementById('themeToggle');
  if(b){b.addEventListener('click',function(){
    var t=root.getAttribute('data-theme')==='dark'?'light':'dark';
    root.setAttribute('data-theme',t); localStorage.setItem('pp-theme',t);
  });}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12});
  document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
  var r=document.getElementById('rotator');
  if(r){try{var w=JSON.parse(r.getAttribute('data-words')||'[]');var i=0;
    if(w.length>1){setInterval(function(){i=(i+1)%w.length;r.style.opacity=0;
      setTimeout(function(){r.textContent=w[i];r.style.opacity=1;},250);},2400);}}catch(e){}}
})();
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&'
         'family=Sora:wght@600;700;800&display=swap" rel="stylesheet">')

def build(resume_path, template, theme, accent, out, base_dir):
    resume = derive(sanitize(json.load(open(resume_path, encoding='utf-8'))))
    tdir = os.path.join(base_dir, 'templates', template)
    base_css = open(os.path.join(base_dir, 'assets', 'base.css'), encoding='utf-8').read()
    extra_path = os.path.join(tdir, 'extra.css')
    extra_css = open(extra_path, encoding='utf-8').read() if os.path.exists(extra_path) else ''
    js_path = os.path.join(tdir, 'extra.js')
    extra_js = open(js_path, encoding='utf-8').read() if os.path.exists(js_path) else ''
    body = mustache(open(os.path.join(tdir, 'body.html'), encoding='utf-8').read(), resume)

    accent_ink = ink_for(accent)
    accent_css = f":root{{--accent:{accent};--accent-ink:{accent_ink};}}"
    title = html.escape(f"{resume.get('name','')} | {resume.get('headline','')}")
    desc = html.escape(resume.get('summary', resume.get('about', '')))[:160]

    # auto favicon (monogram) + Open Graph for shareability
    ini = html.escape(resume.get('_initials', ''))
    fav = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
           f"<rect rx='22' width='100' height='100' fill='{accent}'/>"
           f"<text x='50' y='50' dy='.35em' text-anchor='middle' font-family='sans-serif' "
           f"font-size='46' font-weight='700' fill='{accent_ink}'>{ini}</text></svg>")
    favicon = "data:image/svg+xml," + quote(fav)
    og = (f'<meta property="og:title" content="{title}">'
          f'<meta property="og:description" content="{desc}">'
          f'<meta property="og:type" content="website">'
          f'<meta name="theme-color" content="{accent}">')
    if resume.get('photo'):
        og += f'<meta property="og:image" content="{html.escape(resume["photo"])}">'

    out_html = (
        f'<!DOCTYPE html>\n<html lang="en" data-theme="{theme}">\n<head>\n'
        f'<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n<meta name="description" content="{desc}">\n'
        f'<link rel="icon" href="{favicon}">\n{og}\n{FONTS}\n'
        f'<style>\n{base_css}\n{extra_css}\n{accent_css}\n</style>\n</head>\n<body>\n'
        f'{body}\n<script>{JS}\n{extra_js}</script>\n</body>\n</html>\n'
    )
    open(out, 'w', encoding='utf-8').write(out_html)
    # QA: no unresolved tags
    leftover = re.findall(r'\{\{.*?\}\}', body)
    print(f"[ok] wrote {out}  ({len(out_html)} bytes, theme={theme}, accent={accent})")
    if leftover:
        print(f"[warn] {len(leftover)} unresolved tag(s): {leftover[:5]}", file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--resume', required=True)
    ap.add_argument('--template', required=True)
    ap.add_argument('--theme', default='light', choices=['light', 'dark'])
    ap.add_argument('--accent', default='#4f46e5')
    ap.add_argument('--out', default='index.html')
    ap.add_argument('--base-dir', default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    sys.exit(build(a.resume, a.template, a.theme, a.accent, a.out, a.base_dir))
