from dotenv import load_dotenv
import os
import json
import re
import tempfile

# VERY IMPORTANT: load env BEFORE importing other services
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from acrcloud_service import recognize_file
from gemini_service import get_copyright_info

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    # 1. Save uploaded file temporarily
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # 2. Call ACRCloud
    try:
        raw_result = recognize_file(tmp_path)
    finally:
        os.remove(tmp_path)

    # 3. Check recognition status
    status = raw_result.get("status", {})
    if status.get("msg") != "Success":
        return {
            "success": False,
            "message": "Track not recognized",
            "raw": raw_result
        }

    # 4. Parse ACRCloud metadata
    music = raw_result["metadata"]["music"][0]

    title = music.get("title")
    artists = [a["name"] for a in music.get("artists", [])]
    album = music.get("album", {}).get("name")
    release_date = music.get("release_date")
    score = music.get("score")
    acrid = music.get("acrid")

    # 5. Call Gemini for copyright & licensing info
    try:
        raw_gemini = get_copyright_info(
            title=title,
            artists=artists,
            album=album,
            release_date=release_date
        )

        # ---- Clean Gemini Markdown fences ----
        cleaned = raw_gemini.strip()

        # Remove ```json or ``` wrappers
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^```", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        # Parse JSON
        gemini_report = json.loads(cleaned)

    except Exception as e:
        gemini_report = {
            "error": str(e),
            "raw_output": raw_gemini if 'raw_gemini' in locals() else None
        }

    # 6. Return final combined response
    return {
        "success": True,
        "title": title,
        "artists": artists,
        "album": album,
        "release_date": release_date,
        "confidence_score": score,
        "acrid": acrid,
        "copyright_report": gemini_report
    }
