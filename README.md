# LPU HINGLISH COMPLAINT ROUTER
### AI-Powered Campus Complaint Classification and Intelligent Ticket Routing System
**Tagline:** *"Apni Language Mein Complaint. Right Department Tak Direct."*  
**Campus Focus:** Lovely Professional University (LPU), Phagwara, Punjab, India.

> **Disclaimer:** *Prototype demonstration platform. Complaints submitted in this environment are for hackathon demonstration and evaluation purposes and are not officially registered with Lovely Professional University.*

---

## 1. Executive Summary & Problem Statement
Lovely Professional University has a massive campus with over 35,000 students living in residential hostels (BH-1 to BH-8, GH-1 to GH-4), studying across extensive academic blocks (Block 34, Block 38, Block 36, Block 13, etc.), and utilizing shared amenities such as dining halls, libraries, laboratories, and high-density Wi-Fi networks.

Students report daily infrastructure and service issues using informal spoken vernaculars:
- **Hinglish:** *"Bhai hostel ke washroom ka tap 3 din se leak kar rha h."*
- **Romanised Punjabi:** *"Block 34 di wifi kal raat ton nahi chal rahi."*
- **Everyday Hindi:** *"Mess mein khana bahut thanda mil raha hai."*
- **English:** *"Exposed electrical wire near the hostel washroom entrance. Students can get hurt."*

Manual triage is slow, prone to misclassification, and frequently bounces tickets between unrelated departments. **LPU HINGLISH COMPLAINT ROUTER** automates this end-to-end using context-aware Natural Language Processing that extracts campus locations without hallucination, detects urgent safety hazards, identifies duplicates, calculates model uncertainty, and routes tickets into canonical department queues.

---

## 2. Key System Architecture & Capabilities

```
[ Student Informal Complaint (Hinglish / Punjabi / Hindi / English) ]
                           │
                           ▼
          ┌───────────────────────────────────┐
          │  STAGE 1: Language Detection      │
          │  (Hinglish, Punjabi, Hindi, Eng)  │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │  STAGE 2: Entity & Location Extr. │
          │  Campus → Block → Wing → Floor    │
          │  → Room/Facility (Zero Halluc.)   │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │  STAGE 3: Department Classifier   │
          │  (Strict 6 Primary Departments)   │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │  STAGE 4: Urgency & Safety Guard  │
          │  (Low, Medium, High, Critical)    │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │  STAGE 5: Semantic Duplicate Check│
          │  (Jaccard/Cosine Overlap + Loc)   │
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │  STAGE 6: Facility Standardization│
          │  (Informal → Technical Description│
          └─────────────────┬─────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │  STAGE 7: Confidence & Quarantine │
          │  Confidence < 75% or Ambiguous?   │
          └───────────────┬───────┬───────────┘
                          │       │
              High (>=75%)│       │Uncertain (<75%)
                          ▼       ▼
          ┌─────────────────┐   ┌──────────────────────┐
          │ Automated Queue │   │ Human Review Queue   │
          │ (Plumbing, Elec,│   │ (Staff Disambiguation│
          │  Wi-Fi, Mess,   │   │  & Audit Trail)      │
          │  Academic, Misc)│   └──────────┬───────────┘
          └───────────────┬─┘              │
                          │◄───────────────┘
                          ▼
            [ Status Workflow Timeline: ]
   Submitted → Under Review → Assigned → In Progress → Resolved
```

---

## 3. The Six Canonical Departments
The system strictly enforces the six primary departments:
1. **Plumbing:** Water leakage, broken taps, flush valves, washroom drainage, geysers.
2. **Electrical:** Ceiling fans, lights, switchboards, AC cooling, exposed wires, short circuits.
3. **Wi-Fi / IT:** Campus access point drops, slow internet, router reboot, smart classroom AV.
4. **Mess:** Substandard meal temperature, hygiene concerns, kitchen dining amenities.
5. **Academic:** Classroom timetables, faculty coordination, attendance portal, lab manuals.
6. **Other:** Furniture, carpentry, general cleaning, horticulture, lost & found.

---

## 4. The Three Connected Interfaces
All three portals read and write to the same synchronized reactive database in real time:

### A. Student Portal
- **Real-Time Live AI Extraction Card:** As the student types in Hinglish or Punjabi, the AI dynamically extracts Block, Wing, Floor, Room, Facility, and Department with confidence bars before form submission.
- **Location Verification:** Students can review and manually refine the extracted location tags.
- **Live Ticket Tracker:** Interactive visual milestone timeline (`Submitted` → `Under Review` → `Assigned` → `In Progress` → `Resolved`) featuring timestamped technician notes and dual-view comparison of the original message and standardized description.

### B. Department Staff Portal
- Separate tabs for all 6 departments with active queue badges.
- **Manage Ticket Drawer:** View original vernacular alongside formal technical description, update operational statuses, append work order notes (visible instantly to the student), request department transfers, and manage duplicate linkages.

### C. Administration & AI Monitor
- **Executive KPIs:** Total complaints, auto-routing percentage, quarantine queue depth, safety alerts.
- **Interactive Visual Heatmaps:** Department distribution bar charts and campus location hotspots (e.g., Block 34, BH-1, BH-4).
- **Human Review Queue:** Dedicated triage panel with AI uncertainty explanations and 1-click human resolution overrides.
- **AI Performance Benchmark Runner:** Live empirical benchmark test suite executing 20 unseen evaluation complaints live for hackathon judges, measuring accuracy, latency (ms), and cost per query.
- **Configurable Settings:** Sliders for confidence threshold (default 75%) and duplicate threshold (default 70%).

---

## 5. Official Demonstration Test Cases

| Test | Vernacular Input | Expected Dept | Location Extracted | Urgency | Key Capability Demonstrated |
|---|---|---|---|---|---|
| **Test 1** | *"Bhai hostel ke washroom ka tap 3 din se leak kar rha h."* | **Plumbing** | Hostel Washroom | Medium | Hinglish phrasing, plumbing entity mapping |
| **Test 2** | *"Block 34 di wifi kal raat ton nahi chal rahi."* | **Wi-Fi / IT** | Block 34 | Medium | Romanised Punjabi dialect detection (*ton*, *nahi*) |
| **Test 3** | *"Room 412 mein fan kaam nahi kar raha."* | **Electrical** | Room 412 | Medium | Room number parsing & electrical dispatch |
| **Test 4** | *"Mess mein khana bahut thanda mil raha hai."* | **Mess** | Mess Complex | Medium | Food temperature quality grievance |
| **Test 5** | *"Exposed electrical wire near the hostel washroom entrance. Students can get hurt."* | **Electrical** | Hostel Washroom Entrance | **Critical** | **Safety Hazard Detection: YES** (Alert pulse) |
| **Test 6** | *"Sir attendance portal open nahi ho raha."* | **Quarantine** | Online Portal | Medium | **Human Review Queue** (Cross-boundary ambiguity) |

---

## 6. How to Run Locally

### Project Layout
```text
index.html          Main page
css/styles.css      Page styles
js/app.js           Application interactions and behavior
js/theme-init.js    Early theme preference setup
assets/             Images and other static assets
backend/server.py   Optional Python API and local server
```

### Python Local Server with Real AI
```bash
# Windows PowerShell
$env:AI_API_KEY="your-google-ai-studio-api-key"
$env:AI_MODEL="gemini-3.5-flash-lite"  # optional
$env:AI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"  # optional
python backend/server.py
# Open http://localhost:8000 in your browser
```

The demo defaults to Gemini 3.5 Flash-Lite on Google AI Studio's free tier. Create a key at
https://aistudio.google.com/apikey and store it only in the environment or Render's secret settings.
Free-tier limits can reject requests when exceeded, and Google may use free-tier inputs and outputs
to improve its products. Do not submit names, registration numbers, contact details, or confidential
complaints to this demo.

---

## 7. Hackathon Judge Pitch Highlights
1. **Zero Hallucination Guarantee:** Location entities not explicitly present in the student's text are marked `"Not specified"` rather than fabricated.
2. **Safety-First Priority Scoring:** Immediate hazard detection escalates dangerous situations (such as bare wiring) to `Critical` priority with visual safety alerts.
3. **Multi-Dialect Adaptability:** Seamlessly processes Hindi, Hinglish, Romanised Punjabi, and standard English.
4. **Human-in-the-Loop Safeguard:** Transparent uncertainty calculation prevents misrouting by routing ambiguous cases to administrators with clear explanations.
