from flask import Flask, Response
import re
import requests

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def sanitize_description(text):
    # Substitui literalmente os padrões \\n e \\,
    text = text.replace("\\\\n", " ").replace("\\\\,", ",")
    
    # Substitui padrões simples \n e \, também (caso o texto já venha decodificado)
    text = text.replace("\\n", " ").replace("\\,", ",")

    # Remove barras invertidas restantes
    text = text.replace("\\", "")

    # Remove underscores
    text = text.replace("_", "")

    # Simula negrito: **texto** → TEXTO
    text = re.sub(r"\*\*(.*?)\*\*", lambda m: m.group(1).upper(), text)

    # URLs em nova linha
    text = re.sub(r"(https?://[^\s]+)", r"\n\1", text)

    # Remove espaços duplicados
    text = re.sub(r" +", " ", text)

    # Quebra de parágrafo após ponto final (evita URLs)
    text = re.sub(r"\.(\s+)", ".\n\n", text)

    # Remove espaços antes de quebras de linha
    text = re.sub(r" *\n", "\n", text)

    # Remove quebras de linha duplicadas extras (garante apenas 2 no máximo)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

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
