---
name: portfolio-builder
description: Turn anyone's resume (PDF/DOCX/text dropped in a folder, optionally a LinkedIn PDF export) into a polished, single-file "Aurora" portfolio website with a built-in chatbot, then deploy it free to GitHub Pages. Use whenever a user wants a personal site, portfolio, or "website from my resume". Triggers on "portfolio", "personal website", "site from my resume", "build my resume into a website".
---

# Portfolio Builder (Aurora)

Build a premium portfolio from a resume. **The design is fixed in this skill — you NEVER write HTML/CSS.**
Your only jobs: (1) extract the resume into `resume.json`, (2) run `build.py`. Same code + data → identical output.

## Pipeline
```
resume.pdf / linkedin.pdf  --(markitdown: mechanical)-->  raw text
raw text                   --(YOU, the agent: judgment)-->  resume.json
resume.json + theme + accent --(build.py: deterministic)-->  index.html
index.html                 --(you guide)-->  GitHub Pages
```

## Step 0 — Read the resume (do NOT ask the user to paste it)
The user dropped a resume into the working folder. Find and read it yourself:
- List the folder; find `*.pdf` / `*.docx` / `*.txt` / `*.md`. A LinkedIn "Save to PDF" export counts too — merge it.
- Convert: `python3 -m markitdown <file>` (install once if missing: `pip install "markitdown[all]"`).
- Only ask the user for the file if you genuinely can't find one.

## Step 0b - Optional: extract a headshot from the PDF (ToS-safe)
A real photo makes the hero shine. If the user provided a LinkedIn "Save to PDF" export or a resume PDF
that includes a headshot, extract it from the local file:
```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/portfolio-builder/extract_photo.py" <file.pdf> photo.png
```
- On `WROTE photo.png`: set `resume.json` `"photo": "photo.png"` and keep `photo.png` next to `index.html`
  (commit it too when deploying).
- On `NO_PHOTO_FOUND`: try the public GitHub avatar (see below); otherwise leave `photo` empty and the monogram fallback is used.

**Fallback photo from a GitHub link (public, allowed).** Resumes often link GitHub. If no embedded photo was
found and the PDF contains a GitHub profile URL `https://github.com/<username>`, download the public avatar:
```
curl -sL "https://github.com/<username>.png?size=460" -o photo.png
```
If the file is a real photo (a few hundred KB, not a tiny default identicon), set `resume.json` `"photo": "photo.png"`.
- **Never scrape a photo from a LinkedIn URL** (login-gated and against LinkedIn's terms). LinkedIn cannot be
  used as a photo source. Use only a local PDF's embedded image or a public GitHub avatar.
- Needs `pip install pymupdf` (only for this optional step).

## Step 1 — Extract into `resume.json` (robust to messy resumes)
Write a `resume.json` in the working folder following the schema below. This is the ONLY place judgment
lives — handle headingless/two-column/metric-less resumes, reconstruct garbled text, infer structure.
- Write a sharp 1-line `summary` and a fuller `about` if the resume's are weak.
- Pull `metrics` from achievement bullets (e.g. "cut reporting 70%" -> {value:"70%", label:"..."}). Aim for 3.
- Group `skills` into 2-4 categories. Add per-role `tags` (2-3 short metric chips).
- Generate a `chatbot` Q&A set (5 pairs) answering common recruiter questions FROM the resume.
- **Never use em/en dashes (— –)** in any text — use "-" or reword. (build.py also strips them as a backstop.)
- Leave arrays empty if the data isn't there; empty sections are auto-omitted.

### resume.json schema
```json
{
  "name": "", "headline": "", "roles": ["headline variants for the typewriter"],
  "location": "", "photo": "https://... (optional; monogram used if absent)",
  "available": true, "years_experience": "6+",
  "focus": ["3 focus areas"],
  "contact": { "email": "", "phone": "", "links": [{ "label": "LinkedIn", "url": "" }] },
  "summary": "one punchy line", "about": "2-3 sentence paragraph",
  "metrics": [{ "value": "70%", "label": "what it measured" }],
  "experience": [{ "role": "", "company": "", "dates": "2022 - Present",
                   "bullets": ["..."], "tags": ["70% faster"], "logo": "url (optional)" }],
  "projects": [{ "title": "", "tag": "", "description": "", "link": "", "image": "url (optional)" }],
  "skills": [{ "group": "Category", "items": ["skill"], "icon": "ai|chart|cloud|code|shield|users|wrench (optional)" }],
  "education": [{ "degree": "", "school": "", "year": "" }],
  "certifications": [{ "name": "", "issuer": "" }],
  "publications": [{ "title": "", "venue": "", "year": "", "link": "" }],
  "awards": ["..."], "languages": ["..."],
  "testimonials": [{ "quote": "", "author": "" }],
  "chatbot": [{ "q": "What's your strongest skill?", "a": "drawn from the resume" }]
}
```

## Step 2 — Confirm
Show a short summary of what you extracted and ask: **"Got it right? Anything to fix?"** Apply edits to `resume.json`.

## Step 3 — Ask theme + accent (config only)
- **Theme:** light or dark (default: light — it tends to read best).
- **Accent color:** a hex (default `#f59e0b`). Suggest one that fits their field if they don't care.

## Step 4 — Build (deterministic; never hand-edit the output)
```
python3 "${CLAUDE_PLUGIN_ROOT}/skills/portfolio-builder/build.py" \
  --resume resume.json --template aurora --theme light --accent "#f59e0b" --out index.html
```
build.py needs only python3 (no third-party deps).

## Step 5 — Quality pass
- build.py prints `[warn]` if any `{{token}}` is unresolved — there should be none.
- Open `index.html` in the browser so the user sees it.
- To restyle, DO NOT edit HTML — just rerun build.py with a different `--theme` / `--accent`, or fix `resume.json`.

## Step 6 — Deploy free to GitHub Pages (when the user says "deploy")
Non-technical path, no terminal:
1. New **public** repo (suggest `username.github.io` for a root site).
2. Drag-and-drop `index.html` into the repo web UI.
3. Settings → Pages → Source: `main` / root → Save → ~1 min → live URL. Share it.
- If `gh` CLI is available and they prefer, automate it. Backup: Netlify Drop (app.netlify.com/drop).

## What Aurora includes (so you can describe it)
Loading splash, 2-column hero (photo/monogram + quick-facts, typewriter, teaser stats, cursor spotlight),
credibility marquee, bento impact, vertical timeline (company marks + metric chips + "Now"), icon-category
skills, gradient/image project cards, credential badges, education + awards + languages, testimonials,
contact, **client-side chatbot** (answers from your `chatbot` Q&A), scroll-spy nav, light/dark + any accent,
favicon + Open Graph. One self-contained `index.html`, zero runtime dependencies.

## Reusability (the teaching point)
Same skill, any resume: swap the file → new `resume.json` → rerun build.py → new site. The design code never changes.
