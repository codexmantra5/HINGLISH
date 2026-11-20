#!/usr/bin/env python3
"""
LPU HINGLISH COMPLAINT ROUTER - Backend Server
AI-Powered Campus Complaint Classification & Intelligent Ticket Routing System
Lovely Professional University, Phagwara, Punjab
"""

import http.server
import socketserver
import json
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = int(os.getenv("PORT", "8000"))
PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Canonical Primary Departments
PRIMARY_DEPARTMENTS = ["Plumbing", "Electrical", "Wi-Fi / IT", "Mess", "Academic", "Other"]

# Lightweight In-Memory / JSON DB file path
DB_FILE = os.path.join(BACKEND_DIRECTORY, "complaints_database.json")

def load_dotenv():
    env_file = os.path.join(PROJECT_DIRECTORY, ".env")
    if not os.path.exists(env_file):
        return
    try:
        with open(env_file, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass

load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def analyze_complaint(text):
    if not AI_API_KEY:
        raise RuntimeError("AI_API_KEY (or OPENAI_API_KEY) is not configured")

    system_prompt = """You are an expert campus complaint routing system.
Analyze informal complaints in Hinglish, Hindi, Romanised Punjabi, or English.
Return ONLY a valid JSON object, with no markdown or extra text.
Departments: Plumbing, Electrical, Wi-Fi / IT, Mess, Academic, Other.
Extract only location facts explicitly stated. Use "Not specified" for missing values.
Location object keys: campus, block, wing, floor, room, facility.
Priority must be Low, Medium, High, or Critical.
Confidence must be a number between 0 and 1 representing department confidence.
Set safetyAlert true only for an immediate physical safety hazard.
Provide uncertaintyReason when confidence is below 0.75 or intent is genuinely ambiguous."""

    user_prompt = f"""Complaint:
{text}

Return this exact JSON shape:
{{
  "language": "Hinglish|Hindi|Romanised Punjabi|English",
  "department": "Plumbing|Electrical|Wi-Fi / IT|Mess|Academic|Other",
  "confidence": 0.0,
  "uncertain": false,
  "uncertaintyReason": "",
  "priority": "Low|Medium|High|Critical",
  "safetyAlert": false,
  "location": {{
    "campus": "LPU Main Campus",
    "block": "Not specified",
    "wing": "Not specified",
    "floor": "Not specified",
    "room": "Not specified",
    "facility": "Not specified"
  }},
  "standardizedText": "Clear English operational ticket description"
}}"""

    started = time.perf_counter()
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    request = urllib.request.Request(
        f"{AI_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            api_result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AI provider error {exc.code}: {detail}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"AI provider unavailable: {exc.reason}")

    latency_ms = round((time.perf_counter() - started) * 1000)
    content = api_result["choices"][0]["message"]["content"]
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()

    result = json.loads(content)
    if result.get("department") not in PRIMARY_DEPARTMENTS:
        result["department"] = "Other"
    try:
        confidence = max(0.0, min(1.0, float(result.get("confidence", 0))))
    except (TypeError, ValueError):
        confidence = 0.0
    result["confidence"] = confidence
    result["uncertain"] = bool(confidence < 0.75 or result.get("uncertain"))
    if result["uncertain"] and not result.get("uncertaintyReason"):
        result["uncertaintyReason"] = f"Department confidence ({round(confidence * 100)}%) is below the 75% routing threshold."

    usage = api_result.get("usage") or {}
    input_tokens = int(usage.get("prompt_tokens", 0))
    output_tokens = int(usage.get("completion_tokens", 0))
    input_cost = float(os.getenv("AI_INPUT_COST_PER_MILLION", "0.15"))
    output_cost = float(os.getenv("AI_OUTPUT_COST_PER_MILLION", "0.60"))
    cost = (input_tokens / 1_000_000 * input_cost) + (output_tokens / 1_000_000 * output_cost)
    if not input_tokens and not output_tokens:
        estimated_tokens = max(1, (len(system_prompt) + len(user_prompt) + len(content)) // 4)
        cost = estimated_tokens / 1_000_000 * (input_cost + output_cost)

    result["latencyMs"] = latency_ms
    result["cost"] = round(cost, 8)
    result["model"] = AI_MODEL
    return result

class LPURequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_json({
                "aiConfigured": bool(AI_API_KEY),
                "model": AI_MODEL if AI_API_KEY else None,
                "provider": AI_BASE_URL
            })
            return
        if parsed.path == "/api/complaints":
            self.send_json(load_db())
            return
        super().do_GET()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/analyze":
            try:
                length = int(self.headers.get('Content-Length', 0))
                payload = json.loads(self.rfile.read(length).decode('utf-8'))
                text = str(payload.get("text", "")).strip()
                if len(text) < 3:
                    self.send_json({"error": "Complaint text is required"}, 400)
                    return
                self.send_json(analyze_complaint(text))
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON request"}, 400)
            except RuntimeError as exc:
                self.send_json({"error": str(exc)}, 503)
            except (KeyError, json.JSONDecodeError) as exc:
                self.send_json({"error": f"AI returned invalid JSON: {exc}"}, 502)
            return

        if parsed.path == "/api/complaints/submit":
            try:
                length = int(self.headers.get('Content-Length', 0))
                payload = json.loads(self.rfile.read(length).decode('utf-8'))
                text = str(payload.get("text", "")).strip()
                student_name = str(payload.get("studentName", "Anonymous Student"))
                reg_no = str(payload.get("regNo", ""))
                if len(text) < 5:
                    self.send_json({"error": "Complaint text is required"}, 400)
                    return
                analysis = analyze_complaint(text)
                db = load_db()
                ticket_id = f"LPU-HCR-{datetime.now().year}-{str(len(db) + 1).zfill(3)}"
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                ticket = {
                    "id": ticket_id,
                    "studentName": student_name,
                    "regNo": reg_no,
                    "originalText": text,
                    "standardizedText": analysis["standardizedText"],
                    "language": analysis["language"],
                    "department": analysis["department"],
                    "confidence": analysis["confidence"],
                    "uncertain": analysis["uncertain"],
                    "uncertaintyReason": analysis.get("uncertaintyReason", ""),
                    "priority": analysis["priority"],
                    "safetyAlert": analysis["safetyAlert"],
                    "location": analysis["location"],
                    "status": "Under Review" if analysis["uncertain"] else "Submitted",
                    "submittedAt": date_str,
                    "latencyMs": analysis["latencyMs"],
                    "cost": analysis["cost"],
                    "model": analysis["model"],
                    "staffNotes": [{"time": date_str, "note": f"LLM routed to {analysis['department']} with {round(analysis['confidence'] * 100)}% confidence."}]
                }
                db.insert(0, ticket)
                save_db(db)
                self.send_json(ticket, 201)
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON request"}, 400)
            except RuntimeError as exc:
                self.send_json({"error": str(exc)}, 503)
            except (KeyError, json.JSONDecodeError) as exc:
                self.send_json({"error": f"AI returned invalid JSON: {exc}"}, 502)
            return

        self.send_error(404, "Endpoint Not Found")

if __name__ == "__main__":
    print("=" * 60)
    print("LPU HINGLISH COMPLAINT ROUTER - Multilingual AI Server")
    print("Tagline: 'Apni Language Mein Complaint. Right Department Tak Direct.'")
    print(f"Serving at: http://localhost:{PORT}")
    if not AI_API_KEY:
        print("AI NOT CONFIGURED: add AI_API_KEY to the project .env file")
    print("=" * 60)
    with socketserver.TCPServer(("", PORT), LPURequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
