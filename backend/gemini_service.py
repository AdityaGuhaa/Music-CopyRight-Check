import google.generativeai as genai
import os

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a supported model
model = genai.GenerativeModel("gemini-2.5-flash")


def get_copyright_info(title, artists, album, release_date):
    artist_str = ", ".join(artists)

    prompt = f"""
You are a professional music copyright and licensing researcher.

Given the following song metadata:

Title: {title}
Artist(s): {artist_str}
Album: {album}
Release Date: {release_date}

Your task is to return ONLY valid JSON, and NOTHING ELSE.

You must return a JSON object with EXACTLY the following top-level fields:

- publisher                -> list of objects OR list of strings
- master_rights_holder    -> object OR list of objects OR list of strings
- pros                     -> list of objects OR list of strings
- licensing_sources        -> object with:
      - composition        -> list of objects
      - master_recording  -> list of objects
- source_links             -> list of strings

Each object in licensing_sources lists must have:
- type
- organization
- url

Rules:

1. ALWAYS include all fields, even if empty.
2. If information is not available, return empty lists, not explanations.
3. Do NOT include any text outside the JSON.
4. Do NOT include markdown.
5. Do NOT include comments.
6. The output must be directly parseable by json.loads().

Example output format:

{{
  "publisher": ["Example Publishing"],
  "master_rights_holder": ["Example Records"],
  "pros": ["ASCAP", "BMI"],
  "licensing_sources": {{
    "composition": [
      {{
        "type": "Public Performance License",
        "organization": "ASCAP",
        "url": "https://www.ascap.com/licensing"
      }}
    ],
    "master_recording": [
      {{
        "type": "Synchronization License",
        "organization": "Example Records",
        "url": "https://www.example.com/licensing"
      }}
    ]
  }},
  "source_links": [
    "https://repertoire.bmi.com",
    "https://www.ascap.com/repertory"
  ]
}}

Now return the JSON for the given song.
"""

    response = model.generate_content(prompt)

    # IMPORTANT: return raw text, main.py will clean & parse
    return response.text
