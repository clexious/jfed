from flask import Flask, Response
import re
import requests
import os
from html import escape  # Para limpar caracteres especiais HTML

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def clean_text(text):
    # Aqui você pode adicionar qualquer lógica para limpar ou formatar o texto
    text = text.strip()  # Remove espaços em branco extras
    text = re.sub(r"\n", " ", text)  # Substitui quebras de linha por espaços
    return text

def generate_html_from_text(text):
    # Converte texto em HTML (aqui você pode expandir conforme necessário)
    text = escape(text)  # Escapa caracteres especiais
    html_text = f"<p>{text}</p>"
    return html_text

def get_modified_ics():
    try:
        response = requests.get(ICS_SOURCE_URL)
        content = response.text
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("DESCRIPTION:"):
                raw_text = line[len("DESCRIPTION:"):]
                
                # Limpa o texto
                clean_text_content = clean_text(raw_text)
                
                # Gera o texto HTML
                html_text = generate_html_from_text(clean_text_content)
                
                # Adiciona as linhas modificadas
                new_lines.append(f"DESCRIPTION:{clean_text_content}")
                new_lines.append(f"X-ALT-DESC;FMTTYPE=text/html:{html_text}")
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
