🎵 AI Music Copyright Checker

An end-to-end prototype that identifies a song from an uploaded audio file and returns copyright ownership, performing rights organizations, and licensing paths using a combination of audio fingerprinting (ACRCloud) and Large Language Models (Google Gemini).

This project demonstrates how modern AI systems can be combined with classical music recognition APIs to build a practical copyright intelligence tool for creators, developers, and platforms.

⸻

🚀 What This Project Does
	1.	User uploads an audio file (MP3, WAV, etc.) from the browser.
	2.	Backend sends the audio to ACRCloud for music recognition.
	3.	Once the track is identified, metadata is sent to Google Gemini.
	4.	Gemini returns structured JSON containing:
	•	Composition publishers
	•	Master recording rights holders (labels)
	•	Performing Rights Organizations (PROs)
	•	Where licenses can be obtained
	•	Source links
	5.	Backend normalizes this data into a stable schema.
	6.	Frontend renders a clean, human-readable copyright & licensing report.

In short:

🎧 Audio → 🔍 ACRCloud → 🧠 Gemini → 📜 Structured Copyright Report

⸻

🧠 Core Ideas & Approach

This project was designed around three key principles:

1. Separation of Concerns
	•	ACRCloud is responsible only for identifying the song.
	•	Gemini is responsible only for researching copyright & licensing.
	•	The backend is responsible for:
	•	Cleaning LLM output
	•	Enforcing a fixed schema
	•	Never crashing on bad AI output

2. Defensive AI Engineering

LLMs are unpredictable. To make this production-safe, the backend:
	•	Removes markdown fences from Gemini output
	•	Handles:
	•	Empty responses
	•	Invalid JSON
	•	JSON-as-string
	•	Wrong data types
	•	Enforces a stable output schema for the frontend

This ensures:

❌ The backend never crashes
❌ The frontend never breaks
✅ The API always returns valid JSON

3. Stable Frontend Contract

The frontend does not depend on Gemini’s raw output.

Instead, it consumes a normalized schema:

{
  "publisher": ["..."],
  "master_rights_holder": ["..."],
  "pros": ["..."],
  "licensing_paths": {
    "composition": ["..."],
    "master_recording": ["..."]
  },
  "source_links": ["..."]
}

This makes the UI stable even if Gemini changes its formatting.

⸻

🏗️ System Architecture

Browser (index.html + app.js)
        │
        ▼
 FastAPI Backend (main.py)
        │
        ├── ACRCloud → Identify song
        │
        └── Gemini → Copyright research
                │
                ▼
        Normalized JSON Response
                │
                ▼
          Frontend UI


⸻

🛠️ Tech Stack

Backend
	•	Python 3.10+
	•	FastAPI – REST API framework
	•	ACRCloud API – Music recognition
	•	Google Generative AI (Gemini) – Copyright research
	•	python-dotenv – Environment variable management

Frontend
	•	HTML / CSS / Vanilla JavaScript
	•	Fetch API for file upload & API calls

AI Model
	•	gemini-2.5-flash

⸻

📁 Project Structure

music-cr-checker/
│
├── main.py               # FastAPI backend
├── gemini_service.py    # Gemini prompt & API wrapper
├── acrcloud_service.py  # ACRCloud integration
│
├── index.html           # Frontend UI
├── app.js               # Frontend logic
├── style.css            # Styling
│
├── .env                 # API keys (not committed)
└── README.md


⸻

⚙️ Setup Instructions

1. Clone the Repository

git clone https://github.com/your-username/music-cr-checker.git
cd music-cr-checker

2. Create Virtual Environment

python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

3. Install Dependencies

pip install fastapi uvicorn python-dotenv google-generativeai requests

4. Set Environment Variables

Create a .env file:

ACRCLOUD_ACCESS_KEY=your_acrcloud_key
ACRCLOUD_SECRET_KEY=your_acrcloud_secret
ACRCLOUD_HOST=your_acrcloud_host

GEMINI_API_KEY=your_gemini_api_key

5. Run Backend

uvicorn main:app --reload

Backend will run at:

http://127.0.0.1:8000

6. Run Frontend

Simply open:

index.html

in your browser (or serve via a simple HTTP server).

⸻

🔌 API Endpoint

POST /analyze-audio

Request:
	•	multipart/form-data
	•	Field: file → audio file

Response (simplified):

{
  "success": true,
  "title": "No Pole",
  "artists": ["Don Toliver"],
  "confidence_score": 100,
  "official_search_links": { ... },
  "copyright_report": {
    "publisher": [...],
    "master_rights_holder": [...],
    "pros": [...],
    "licensing_paths": {
      "composition": [...],
      "master_recording": [...]
    },
    "source_links": [...]
  }
}


⸻

🧩 Key Engineering Challenges Solved

1. Unstable LLM Output

Gemini can return:
	•	Markdown-wrapped JSON
	•	Invalid JSON
	•	JSON as a string
	•	Explanations instead of data

Solution:
	•	Strip markdown fences
	•	Use safe_json_loads
	•	Enforce dict type
	•	Controlled fallback on failure

2. Schema Normalization

Gemini may return:
	•	publisher as string, list, or list of objects
	•	Same for pros, master_rights_holder

Solution:
	•	Flatten everything into list[str]
	•	Frontend consumes only normalized data

3. Future-Dated & Unknown Songs

For unreleased or new songs:
	•	Gemini returns empty lists
	•	Backend still returns valid JSON
	•	UI shows “Not available” instead of breaking

⸻

🧪 Example Results

The system works for:
	•	Popular released tracks
	•	Newly released tracks
	•	Future-dated / unreleased tracks

With graceful degradation when data is unavailable.

⸻

⚠️ Limitations
	•	This is a research & prototype tool, not a legal authority.
	•	Licensing information may change over time.
	•	Some songs may have incomplete public data.
	•	Accuracy depends on:
	•	ACRCloud recognition
	•	Public availability of rights data
	•	LLM interpretation

⸻

🔮 Future Improvements

Planned extensions:
	•	Add copyright_status classification
	•	Add confidence scoring for rights certainty
	•	Add PDF / JSON export of reports
	•	Add database logging
	•	Add authentication & rate limiting
	•	Dockerize for deployment
	•	Deploy on cloud (Render / Railway / Fly.io)

⸻

👨‍💻 Author

Aditya Guha
AI & Machine Learning Enthusiast
Computer Science Engineering

This project was built as a fast-paced prototype to demonstrate:
	•	Real-world AI integration
	•	Defensive LLM engineering
	•	Clean API & frontend contracts

⸻

📜 License

This project is for educational and research purposes.
No legal liability is assumed for the use of copyright information.

⸻

If you find this project useful, feel free to ⭐ star the repository and explore further improvements.