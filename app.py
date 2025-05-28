from flask import Flask, Response
import requests
import os

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def get_modified_ics():
    try:
        response = requests.get(ICS_SOURCE_URL)
        content = response.text
        lines = content.splitlines()
        new_lines = []
        x_alt_desc_content = ""

        for line in lines:
            if line.startswith("X-ALT-DESC;FMTTYPE=text/html:"):
                # Extrai o conteúdo do campo X-ALT-DESC
                x_alt_desc_content = line[len("X-ALT-DESC;FMTTYPE=text/html:"):]

            if line.startswith("DESCRIPTION:"):
                # Substitui o conteúdo do campo DESCRIPTION pelo conteúdo do campo X-ALT-DESC
                new_lines.append(f"DESCRIPTION:{x_alt_desc_content}")
            else:
                # Adiciona as outras linhas normalmente
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
