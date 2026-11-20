# LPU Hinglish Complaint Router

A static, browser-only demo for routing campus complaints to six departments:
Plumbing, Electrical, Wi-Fi / IT, Mess, Academic, and Other.

## Demo behavior

- Uses local keyword rules for language hints, department, location, and urgency. It does not call an LLM or a backend API.
- Stores tickets in this browser's local storage; data is not shared across browsers or devices.
- Loads a built-in set of fictional sample tickets on first use. Use **Restore sample data** in Admin settings to reload them.
- Low-confidence or ambiguous complaints are marked for human review.

This is a hackathon prototype, not an official LPU service. The rule-based classification is only a demonstration and may be incorrect. Do not enter real personal or confidential information.

## Run locally

From the project directory, start any static HTTP server, for example:

```powershell
python -m http.server 8000
```

Then open <http://localhost:8000>. The static site is also deployed through GitHub Pages.

## Project layout

```text
index.html
css/styles.css
js/app.js
js/theme-init.js
assets/
.github/workflows/pages.yml
```
