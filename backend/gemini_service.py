import google.generativeai as genai
import os

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a supported model
model = genai.GenerativeModel("gemini-2.5-flash")

def get_copyright_info(title, artists, album, release_date):
    artist_str = ", ".join(artists)

    prompt = f"""
You are a music copyright research assistant.

Given this song:

Title: {title}
Artist(s): {artist_str}
Album: {album}
Release Date: {release_date}

Find and provide:

1. Publisher(s) of the composition
2. Master recording rights holder (label / company)
3. Music rights organizations (ASCAP, BMI, PRS, IPRS, etc.)
4. Where a license can be obtained (official pages or organizations)
5. Provide source links for each fact
6. If information is uncertain, explicitly say so

Return the result in clear JSON with fields:
- publisher
- master_rights_holder
- pros
- licensing_sources
- notes
"""

    response = model.generate_content(prompt)
    return response.text
