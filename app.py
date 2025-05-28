from flask import Flask, Response
import requests
import re

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

# Função para modificar o conteúdo ICS
def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text

        # Substituir tags de formatação HTML por simples textos, removendo os underscores e mantendo as quebras de linha
        ics_content = re.sub(r'_(.*?)_', r'\1', ics_content)  # Remove o itálico (underscore)
        ics_content = re.sub(r'\*\*(.*?)\*\*', r'\1', ics_content)  # Remove o negrito (asterisco duplo)
        ics_content = ics_content.replace("_", "")  # Remove underscores restantes
        ics_content = ics_content.replace("\n", "\r\n")  # Certifica-se de que as quebras de linha estão no formato correto

        # Você pode adicionar mais tratamentos ou modificações no conteúdo ICS aqui

        return ics_content
    else:
        # Retorna um conteúdo ICS básico caso falhe a requisição
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
