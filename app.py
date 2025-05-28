from flask import Flask, Response
import re
import requests
import os

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

# Texto puro
def sanitize_description(text):
    text = text.replace("_", "")
    text = re.sub(r"\*\*(.*?)\*\*", lambda m: m.group(1).upper(), text)
    text = text.replace("\\n", "\n").replace("\\", "")
    return text

# HTML formatado
def generate_html_description(text):
    text = text.replace("_", "")
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(https?://[^\s\\]+)", r'<a href="\1">\1</a>', text)
    text = text.replace("\\n", "<br>").replace("\n", "<br>")
    return f"<html><body>{text}</body></html>"

def get_modified_ics():
    try:
        response = requests.get(ICS_SOURCE_URL)
        content = response.text
        lines = content.splitlines()
        new_lines = []
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith("DESCRIPTION:"):
                raw_text = line[len("DESCRIPTION:"):]
                clean_text = sanitize_description(raw_text)
                html_text = generate_html_description(raw_text)

                new_lines.append("DESCRIPTION:" + clean_text)
                new_lines.append("X-ALT-DESC;FMTTYPE=text/html:" + html_text)
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
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
