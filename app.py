from flask import Flask, Response
import requests
import os
import re
import openai  # Para chamar o ChatGPT API

app = Flask(__name__)

# Sua chave da API OpenAI
openai.api_key = "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"

ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=eyJwayI6ImNpbmNpbm5hdGkiLCJjb21tdW5pdHlfY2FsZW5kYXIiOnRydWV9:1u6suP:rmMCXGHV2YBVnadKQmYjW-3O19e9UPhzz8f-b-OdUU8&lg=en"

def remove_html_tags(text):
    # Remove todas as tags HTML do texto usando regex
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

def improve_text_with_chatgpt(text):
    try:
        # Limitar o tamanho do texto para não ultrapassar o limite de tokens do ChatGPT
        if len(text) > 1000:
            text = text[:1000]  # Reduz o texto se for muito grande

        # Solicitar melhoria do texto para o ChatGPT
        response = openai.Completion.create(
            engine="gpt-4",  # Usando o modelo GPT-4
            prompt=f"Melhore a formatação deste texto sem alterar as palavras:\n\n{text}",
            max_tokens=1000,  # Limitar o tamanho da resposta
            temperature=0.7,  # Criatividade do modelo
        )

        # Exibir a resposta da API para depuração
        print("Resposta do ChatGPT:", response)

        # Extrair a resposta gerada
        improved_text = response.choices[0].text.strip()
        return improved_text
    except Exception as e:
        # Exibir a exceção detalhada para diagnóstico
        print(f"Erro ao processar o texto com o ChatGPT: {str(e)}")
        return f"Erro ao processar o texto com o ChatGPT: {str(e)}"

def get_modified_ics():
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
        print(f"Erro ao obter o conteúdo ICS: {str(e)}")
        return f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:ERROR\nDESCRIPTION:{str(e)}\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
