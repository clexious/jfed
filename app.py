import re
import requests

def clean_description(text):
    # Junta quebras de linha dentro do campo DESCRIPTION quando não são finais de frase
    def fix_linebreaks(desc):
        return re.sub(
            r'(?<![\.\?!:])\n(?=[a-z0-9])',
            ' ',
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

        # Corrige quebras de linha no DESCRIPTION
        ics_content = clean_description(ics_content)

        # Adiciona quebra de linha antes de URLs (opcional)
        ics_content = re.sub(r'(https?://[^\s]+)', r'\n\1', ics_content)

        # Remove todos os underlines
        ics_content = ics_content.replace('_', '')

        return ics_content
    else:
        return "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App//EN\nEND:VCALENDAR"
