from flask import Flask, Response
import re
import requests

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def clean_description(text):
    # Função que limpa e reestrutura o conteúdo do campo DESCRIPTION
    def fix_description(desc):
        # Remove sublinhado
        desc = desc.replace('_', '')

        # Divide por parágrafos (dupla quebra de linha ou linha em branco)
        paragraphs = re.split(r'\n\s*\n', desc)

        cleaned_paragraphs = []
        for para in paragraphs:
            lines = para.strip().split('\n')
            new_lines = []

            buffer = ""
            for line in lines:
                if re.match(r'^https?://', line.strip()):
                    # Se a linha anterior tiver conteúdo acumulado, adiciona
                    if buffer:
                        new_lines.append(buffer.strip())
                        buffer = ""
                    new_lines.append(line.strip())  # mantém a URL separada
                else:
                    buffer += ' ' + line.strip()
            if buffer:
                new_lines.append(buffer.strip())

            cleaned_paragraphs.append('\n'.join(new_lines))

        # Rejunta com \n\n para manter parágrafos separados
        return '\n\n'.join(cleaned_paragraphs)

    def replace_description(match):
        desc = match.group(1)
        fixed = fix_description(desc)
        return f'DESCRIPTION:{fixed}'

    return re.sub(r'DESCRIPTION:(.*?)(?=\n[A-Z\-]+:|\nEND:VEVENT)', replace_description, text, flags=re.DOTALL)

def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text

        # Corrige o campo DESCRIPTION
        ics_content = clean_description(ics_content)

        return ics_content
    else:
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
