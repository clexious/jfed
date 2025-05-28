from flask import Flask, Response
import requests
import re

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

# Função para modificar e preservar todos os eventos no ICS
def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text
        
        # Verificar se o conteúdo do ICS está presente
        if "BEGIN:VEVENT" in ics_content:
            events = []
            event_blocks = re.split(r"(BEGIN:VEVENT.*?END:VEVENT)", ics_content, flags=re.DOTALL)
            for event in event_blocks:
                if event.strip():
                    # Processar cada evento separadamente
                    event = re.sub(r'_(.*?)_', r'\1', event)  # Remover o itálico
                    event = re.sub(r'\*\*(.*?)\*\*', r'\1', event)  # Remover o negrito
                    event = event.replace("\n", "\r\n")  # Garantir a quebra de linha correta
                    events.append(event)
            
            # Reunir todos os eventos processados de volta
            modified_ics_content = "".join(events)
        else:
            # Se não houver eventos no ICS, retornar um conteúdo ICS vazio
            modified_ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"
        
        return modified_ics_content
    else:
        # Se a requisição falhar, retornar um conteúdo ICS vazio
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
