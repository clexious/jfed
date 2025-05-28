from flask import Flask, Response
import re
import requests

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def clean_description(text):
    # Junta quebras de linha dentro do campo DESCRIPTION quando não são finais de frase
    def fix_linebreaks(desc):
        return re.sub(
            r'(?<![\.\?!:])\n(?=[a-z0-9])',  # quebra de linha antes de letra minúscula/número
            ' ',  # substitui por espaço
            desc
        )

    # Expressão regular para encontrar o campo DESCRIPTION
    def replace_description(match):
        desc_content = match.group(1)
        fixed_content = fix_linebreaks(desc_content)
        return f'DESCRIPTION:{fixed_content}'

    # Aplica a substituição para cada campo DESCRIPTION
    return re.sub(r'DESCRIPTION:(.*?)(?=\n[A-Z\-]+:)', replace_description, text, flags=re.DOTALL)

def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text

        # Limpa quebras e formatações em DESCRIPTION
        ics_content = clean_description(ics_content)

        # Adiciona quebra de linha antes de URLs
        ics_content = re.sub(r'(https?://[^\s]+)', r'\n\1', ics_content)

        # Remove todos os underscores
        ics_content = ics_content.replace('_', '')

        return ics_content
    else:
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
