---
description: Build a polished Aurora portfolio website from a resume in this folder, then deploy it free.
---

Run the **portfolio-builder** skill end to end:

1. Find a resume file in the current folder (`*.pdf` / `*.docx` / `*.txt` / `*.md`, plus a LinkedIn PDF
   export if present) and read it with `python3 -m markitdown`. Do NOT ask the user to paste their resume.
2. Extract everything into `resume.json` per the skill's schema (write a sharp summary, pull metrics,
   group skills, add per-role tags, and generate the chatbot Q&A). Never use em/en dashes.
3. Show a short summary to confirm; apply any fixes.
4. Ask for theme (light/dark, default light) and accent color (default #f59e0b).
5. Build deterministically — never hand-edit HTML:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/portfolio-builder/build.py" --resume resume.json --template aurora --theme <light|dark> --accent "<hex>" --out index.html`
6. Open it; when the user is ready, deploy to GitHub Pages and share the live link.

Optional preferences from the user: $ARGUMENTS
