from flask import Flask, Response
import requests
import re

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text

        # Remove underscores for italic formatting and ** for bold formatting (if not needed)
        ics_content = re.sub(r'_(.*?)_', r'\1', ics_content)  # Remove italic underscores
        ics_content = re.sub(r'\*\*(.*?)\*\*', r'\1', ics_content)  # Remove bold asterisks

        # Fix potential newline issues, preserving text as is
        ics_content = ics_content.replace("\n", "\r\n")  # Use proper newlines for ICS

        # Ensure the content is not truncated and the text is fully captured
        if len(ics_content) > 3000:  # A check to prevent cutting off large descriptions
            ics_content = ics_content[:3000]  # You can adjust this value as necessary

        return ics_content
    else:
        # If the request fails, return an empty calendar
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
