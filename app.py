import requests
import os
import re
import openai  # Para chamar o ChatGPT API
from flask import Flask, Response

app = Flask(__name__)

# Sua chave da API OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY"  # Substitua com sua chave de API real

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def remove_html_tags(text):
    """Remove todas as tags HTML do texto usando regex."""
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

def improve_text_with_chatgpt(text):
    """Usa o ChatGPT para melhorar a formatação do texto sem alterar as palavras."""
    try:
        # Usando a nova API (openai.Completion.create)
        response = openai.Completion.create(
            model="gpt-4",  # Especificando o modelo
            prompt=f"Melhore a formatação deste texto sem alterar as palavras:\n\n{text}",
            max_tokens=1000,  # Limitar o tamanho da resposta
            temperature=0.7,  # Criatividade do modelo
        )
        # Extrair o texto melhorado da resposta
        improved_text = response['choices'][0]['text'].strip()
        return improved_text
    except Exception as e:
        return f"Erro ao processar o texto com o ChatGPT: {str(e)}"

def get_modified_ics():
    """Modifica o conteúdo do feed ICS com o texto melhorado pelo ChatGPT."""
    try:
        response = requests.get(ICS_SOURCE_URL)
        content = response.text
        lines = content.splitlines()
        new_lines = []

        for line in lines:
            if line.startswith("DESCRIPTION:"):
                # Extrai o conteúdo do campo DESCRIPTION
                description_content = line[len("DESCRIPTION:"):]

                # Remove as tags HTML do conteúdo
                description_content = remove_html_tags(description_content)

                # Melhora a formatação do conteúdo com o ChatGPT
                description_content = improve_text_with_chatgpt(description_content)

                # Substitui o conteúdo do campo DESCRIPTION com o texto melhorado
                new_lines.append(f"DESCRIPTION:{description_content}")
            else:
                # Adiciona as outras linhas normalmente
                new_lines.append(line)

        return "\n".join(new_lines)

    except Exception as e:
        return f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:ERROR\nDESCRIPTION:{str(e)}\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    """Retorna o feed ICS modificado."""
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
