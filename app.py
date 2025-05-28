from flask import Flask, Response
import requests
import re

app = Flask(__name__)

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

# Função para processar o feed ICS
def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text
        
        # Verificar se o conteúdo ICS contém eventos
        if "BEGIN:VEVENT" in ics_content:
            # Encontrar todos os blocos de eventos
            event_blocks = re.findall(r"(BEGIN:VEVENT.*?END:VEVENT)", ics_content, flags=re.DOTALL)
            
            # Processar cada evento individualmente
            processed_events = []
            for event in event_blocks:
                # Remover formatação indesejada
                event = re.sub(r'_(.*?)_', r'\1', event)  # Remove o itálico
                event = re.sub(r'\*\*(.*?)\*\*', r'\1', event)  # Remove o negrito
                event = event.replace("\n", "\r\n")  # Garantir as quebras de linha corretas

                # Adicionar o evento processado à lista de eventos
                processed_events.append(event)
            
            # Reunir todos os eventos em um único conteúdo ICS
            modified_ics_content = "".join(processed_events)
        else:
            # Caso não haja eventos, retornar um conteúdo ICS básico
            modified_ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"
        
        return modified_ics_content
    else:
        # Caso a requisição falhe, retornar um conteúdo ICS básico
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
