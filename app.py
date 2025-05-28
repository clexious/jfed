from flask import Flask, Response
import requests
import re

def clean_description(text):
    # Junta quebras de linha dentro do campo DESCRIPTION quando não são finais de frase
    def fix_linebreaks(desc):
        # Substitui quebras de linha seguidas por letras minúsculas ou espaços
        return re.sub(
            r'(?<![\.\?!:])\n(?=[a-z0-9])',  # quebra de linha que não segue pontuação e precede letra minúscula/número
            ' ',  # substitui por espaço
            desc
        )

    # Expressão regular para encontrar o campo DESCRIPTION
    def replace_description(match):
        desc_full = match.group(0)
        desc_content = match.group(1)
        fixed_content = fix_linebreaks(desc_content)
        return f'DESCRIPTION:{fixed_content}'

    return re.sub(r'DESCRIPTION:(.*?)(?=\n[A-Z\-]+:)', replace_description, text, flags=re.DOTALL)

def get_modified_ics():
    response = requests.get(ICS_SOURCE_URL)
    if response.status_code == 200:
        ics_content = response.text

        # Corrige quebras de linha e melhora URLs
        ics_content = clean_description(ics_content)

        # Torna URLs mais visíveis (opcional)
        ics_content = re.sub(r'(https?://[^\s]+)', r'\n\1', ics_content)

        return ics_content
    else:
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"
