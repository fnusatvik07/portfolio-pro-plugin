<div align="center">

# Portfolio Pro

**Turn any resume into a premium portfolio website. No coding.**

Drop a resume in a folder, answer three quick prompts, and get a polished single-file site
(light or dark, your accent color) with a built-in chatbot, then deploy it free with one step.

![License](https://img.shields.io/badge/license-MIT-black)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-d97757)
![Zero deps](https://img.shields.io/badge/output-single%20HTML%20file-2ea44f)
![Deploy](https://img.shields.io/badge/deploy-GitHub%20Pages-0969da)

</div>

---

## Preview

| Light | Dark |
| :---: | :---: |
| ![Light](screenshots/hero-light.png) | ![Dark](screenshots/hero-dark.png) |

<details>
<summary><b>Full page &amp; mobile</b></summary>

| Full page (light) | Full page (dark) |
| :---: | :---: |
| ![Full light](screenshots/full-light.png) | ![Full dark](screenshots/full-dark.png) |

<img src="screenshots/mobile.png" width="280" alt="Mobile dark"> <img src="screenshots/mobile-light.png" width="280" alt="Mobile light">

</details>

> Demo uses a fictional person ("Maya Sterling") and fictional companies.

---

## Install

### Claude Code  (recommended)
Run as **two separate messages**:
```
/plugin marketplace add https://github.com/fnusatvik07/portfolio-pro-plugin
```
```
/plugin install portfolio-pro@claude4everyone
```
Then use it any time with `/portfolio` (or just say *"build a portfolio from the resume in this folder"*).

### Any other coding agent  (Codex, Cursor, Gemini CLI, Cline, Copilot agent mode, ...)
The skill is plain Markdown + a Python script, so any agent with **file + shell access** can run it:
```
git clone https://github.com/fnusatvik07/portfolio-pro-plugin
```
Then tell your agent:
> Read `portfolio-pro/skills/portfolio-builder/SKILL.md` and follow it to build a portfolio from my resume in this folder.

---

## Use it

1. Make a folder and drop your **resume** in it (`resume.pdf` - PDF, DOCX, or TXT). Optionally add a LinkedIn
   "Save to PDF" export; it gets merged in.
2. Run `/portfolio` (or point your agent at `SKILL.md`).
3. Answer three prompts:
   - **Theme** - light · dark · auto
   - **Accent** - a preset (amber, sky, violet, emerald, rose, indigo, teal, slate, ...), any `#hex`, or `auto` (matches your photo)
   - **Font** - default · serif · grotesk
4. It builds `index.html` and opens it. Say **"deploy"** and it publishes to GitHub Pages and returns your **live URL**.

---

## Features

- **One self-contained `index.html`** - inline CSS/JS, zero runtime dependencies, works for years.
- **Deterministic** - the design is fixed in the plugin; the agent only writes a `resume.json` and runs the
  renderer, so the same input always yields the same output.
- **Designed sections** - animated hero, bento impact metrics, vertical career timeline, icon-grouped skills,
  project cards with tech stack, certifications, services, speaking, testimonials, education.
- **Built-in chatbot** - answers visitor questions from your resume. Fully client-side, no backend, no API key.
- **Smart photo sourcing** - embedded PDF image -> public GitHub avatar -> Gravatar (email) -> a photo you drop
  in -> clean monogram. (LinkedIn is never scraped: login-gated and against its terms.)
- **Themeable** - light / dark / auto, any accent color (or auto from your photo), three font pairings.
- **Share-ready** - favicon, Open Graph, JSON-LD, print stylesheet, and a "Download CV" button.
- **One-step deploy** - automated GitHub Pages publish with your live URL.

---

## Deploy

Say **"deploy"**. The first time, connect GitHub once:

- **Easiest:** run `gh auth login` (stored securely, reused automatically), or
- **Token:** create one at `github.com/settings/tokens` with `repo` scope and pass it as `GH_TOKEN`.

After that, every deploy is a single step and returns `https://<you>.github.io/<repo>/`.
Prefer no GitHub? Drag the folder to [Netlify Drop](https://app.netlify.com/drop).

---

## Requirements

| For | Need |
| --- | --- |
| Building | `python3` (no third-party packages) |
| Reading PDF / DOCX | `pip install "markitdown[all]"` (auto-installed on first run) |
| `auto` accent ("match my photo") | `pip install pillow` |
| Headshot from PDF | `pip install pymupdf` |
| Automated deploy | GitHub CLI (`gh`) or a `repo`-scoped token |

---

## License

MIT © fnusatvik07
