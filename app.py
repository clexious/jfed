from flask import Flask, Response
import re
import requests

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def sanitize_description(text):
    # Remove underscores
    text = text.replace("_", "")
    
    # Substitui **texto** por TEXTO (negrito simulado)
    def bold_replacer(match):
        return match.group(1).upper()

    text = re.sub(r"\*\*(.*?)\*\*", bold_replacer, text)
    
    # Garante que URLs fiquem em nova linha (ajuda na leitura)
    url_pattern = r"(https?://[^\s\\]+)"
    text = re.sub(url_pattern, r"\n\1", text)

    # Limpeza extra
    text = text.replace("\\n", "\n").replace("\\", "")
    
    return text
    
   

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
                new_lines.append("DESCRIPTION:" + clean_text)
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
