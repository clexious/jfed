from flask import Flask, Response
import re
import requests

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def sanitize_description(text):
    text = text.replace("_", "")
    
    def bold_replacer(match):
        return match.group(1).upper()
    text = re.sub(r"\*\*(.*?)\*\*", bold_replacer, text)

    text = text.replace("\\,", ",")
    text = text.replace("\\n", " ").replace("\\", " ")

    url_pattern = r"(https?://[^\s]+)"
    text = re.sub(url_pattern, r"\n\1", text)

    text = re.sub(r" +", " ", text)
    text = re.sub(r"(?<!\w)(\.)(\s+)", r".\n\n", text)
    text = re.sub(r" *\n", "\n", text)

    paragraphs = [f"<p>{line.strip()}</p>" for line in text.strip().split("\n\n") if line.strip()]
    return "\n".join(paragraphs)

def extract_organizer(description):
    match = re.search(r"Organized by:\s*(.*)", description, re.IGNORECASE)
    if match:
        organizer_line = match.group(1)
        organizer_line = organizer_line.split("\n")[0]
        return organizer_line.strip().replace("\\", "")
    return ""

def get_modified_ics():
    try:
        response = requests.get(ICS_SOURCE_URL)
        content = response.text
        lines = content.splitlines()
        new_lines = []

        for line in lines:
            if line.startswith("DESCRIPTION:"):
                text = line[len("DESCRIPTION:"):]
                clean_text = sanitize_description(text)
                organizer = extract_organizer(clean_text)
                new_lines.append("DESCRIPTION:" + clean_text)
                if organizer:
                    new_lines.append("ORGANIZER:" + organizer)
            else:
                new_lines.append(line)

        return "\n".join(new_lines)

    except Exception as e:
        return f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:ERROR\nDESCRIPTION:{str(e)}\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
