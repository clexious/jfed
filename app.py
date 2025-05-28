from flask import Flask, Response
import re
import requests

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def clean_description(text):
    def fix_description(desc):
        # Remove soft breaks do formato .ics (linha quebrada com "=" no final)
        desc = re.sub(r'=\r?\n', '', desc)

        # Remove underscores
        desc = desc.replace('_', '')

        # Divide por parágrafos (linhas em branco)
        paragraphs = re.split(r'\n\s*\n', desc)

        cleaned_paragraphs = []
        for para in paragraphs:
            # Remove quebras de linha dentro do parágrafo e espaços duplicados
            single_line = ' '.join(para.strip().splitlines())
            single_line = re.sub(r'\s{2,}', ' ', single_line)
            cleaned_paragraphs.append(single_line.strip())

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

        # Corrige DESCRIPTIONs
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
