from dotenv import load_dotenv
import os
import json
import re
import tempfile
from urllib.parse import quote_plus
from typing import Any

# VERY IMPORTANT: load env BEFORE importing other services
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from acrcloud_service import recognize_file
from gemini_service import get_copyright_info

app = FastAPI()

# ✅ CORS: allow frontend (localhost, file://, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # for dev; restrict later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


def build_official_search_links(title: str, artists: list[str]):
    query = f"{title} {' '.join(artists)}"
    q = quote_plus(query)

    return {
        "bmi": f"https://repertoire.bmi.com/Search/Search?Main_Search_Text={q}",
        "ascap": f"https://www.ascap.com/repertory#/ace/search/title/{q}",
        "socan": f"https://www.socan.com/jsp/en/mem/pubRepertoireSearch.jsp?searchTerm={q}"
    }


def safe_json_loads(text: str) -> Any:
    """
    Robust JSON loader for LLM output:
    - handles empty
    - handles JSON object
    - handles JSON string that contains JSON
    - handles garbage safely
    """
    if not text or not text.strip():
        raise ValueError("Gemini returned empty response")

    try:
        obj = json.loads(text)
    except Exception as e:
        raise ValueError(f"Gemini returned invalid JSON: {text[:200]}")

    # If Gemini returned JSON-as-string, parse again
    if isinstance(obj, str):
        try:
            obj2 = json.loads(obj)
            obj = obj2
        except Exception:
            raise ValueError(f"Gemini returned JSON string but inner parse failed: {obj[:200]}")

    return obj


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

    # 5. Generate official PRO search links
    official_search_links = build_official_search_links(title, artists)

    # 6. Call Gemini for copyright & licensing info
    try:
        raw_gemini = get_copyright_info(
            title=title,
            artists=artists,
            album=album,
            release_date=release_date
        )

        # ---- Clean Gemini Markdown fences ----
        cleaned = raw_gemini.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^```", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        # ---- Robust JSON parsing ----
        raw_report = safe_json_loads(cleaned)

        # ---- Final guard: must be dict ----
        if not isinstance(raw_report, dict):
            raise ValueError(f"Gemini returned non-dict JSON: type={type(raw_report)}")

        # ===========================
        # 🔧 FLATTEN STRUCTURED DATA
        # ===========================

        # -------- Publishers --------
        publishers_raw = raw_report.get("publisher") or raw_report.get("publishers") or []
        publishers: list[str] = []

        if isinstance(publishers_raw, list):
            for p in publishers_raw:
                if isinstance(p, dict):
                    name = p.get("name")
                    if name:
                        publishers.append(name)
                elif isinstance(p, str):
                    publishers.append(p)
        elif isinstance(publishers_raw, str):
            publishers.append(publishers_raw)

        # -------- Master Rights Holder --------
        master_raw = (
            raw_report.get("master_rights_holder")
            or raw_report.get("master_rights")
            or raw_report.get("label")
            or raw_report.get("labels")
            or []
        )

        master_rights_holder: list[str] = []

        if isinstance(master_raw, dict):
            name = master_raw.get("name")
            if name:
                master_rights_holder.append(name)
        elif isinstance(master_raw, list):
            for m in master_raw:
                if isinstance(m, dict):
                    name = m.get("name")
                    if name:
                        master_rights_holder.append(name)
                elif isinstance(m, str):
                    master_rights_holder.append(m)
        elif isinstance(master_raw, str):
            master_rights_holder.append(master_raw)

        # -------- PROs --------
        pros_raw = (
            raw_report.get("pros")
            or raw_report.get("pro")
            or raw_report.get("performing_rights_organization")
            or []
        )

        pros: list[str] = []

        if isinstance(pros_raw, list):
            for p in pros_raw:
                if isinstance(p, dict):
                    name = p.get("name")
                    if name:
                        pros.append(name)
                elif isinstance(p, str):
                    pros.append(p)
        elif isinstance(pros_raw, str):
            pros.append(pros_raw)

        # ===========================
        # 🔧 HUMAN-READABLE LICENSING PATHS
        # ===========================

        licensing_raw = (
            raw_report.get("licensing_sources")
            or raw_report.get("licensing")
            or raw_report.get("licenses")
            or {}
        )

        licensing_paths = {
            "composition": [],
            "master_recording": []
        }

        if isinstance(licensing_raw, dict):

            # ---- Composition ----
            composition = licensing_raw.get("composition")
            if isinstance(composition, dict):
                for k, v in composition.items():
                    if isinstance(v, str):
                        label = k.replace("_", " ").title()
                        licensing_paths["composition"].append(f"{label}: {v}")
            elif isinstance(composition, list):
                for item in composition:
                    if isinstance(item, dict):
                        org = item.get("organization")
                        typ = item.get("type")
                        if org and typ:
                            licensing_paths["composition"].append(f"{typ}: {org}")

            # ---- Master Recording ----
            master_rec = licensing_raw.get("master_recording")
            if isinstance(master_rec, str):
                licensing_paths["master_recording"].append(master_rec)
            elif isinstance(master_rec, list):
                for item in master_rec:
                    if isinstance(item, dict):
                        org = item.get("organization")
                        typ = item.get("type")
                        if org and typ:
                            licensing_paths["master_recording"].append(f"{typ}: {org}")

        # -------- Source Links --------
        sources_raw = raw_report.get("source_links") or raw_report.get("sources") or []
        source_links: list[str] = []

        if isinstance(sources_raw, list):
            for s in sources_raw:
                if isinstance(s, str):
                    source_links.append(s)
        elif isinstance(sources_raw, str):
            source_links.append(sources_raw)

        # -------- Final normalized report --------
        gemini_report = {
            "publisher": publishers,
            "master_rights_holder": master_rights_holder,
            "pros": pros,
            "licensing_paths": licensing_paths,
            "source_links": source_links
        }

    except Exception as e:
        # 🔴 Controlled fallback — NEVER crash backend
        gemini_report = {
            "publisher": [],
            "master_rights_holder": [],
            "pros": [],
            "licensing_paths": {
                "composition": [],
                "master_recording": []
            },
            "source_links": [],
            "error": str(e)
        }

    # 7. Return final combined response
    return {
        "success": True,
        "title": title,
        "artists": artists,
        "album": album,
        "release_date": release_date,
        "confidence_score": score,
        "acrid": acrid,
        "official_search_links": official_search_links,
        "copyright_report": gemini_report
    }
