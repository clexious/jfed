import os
import openai
import requests
from flask import Flask, Response
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# ICS Feed URL
ICS_SOURCE_URL = "https://jlive.app/markets/cincinnati/ics-feed/feed.ics?token=your_token&lg=en"

def improve_text_with_chatgpt(text):
    """Enhance text formatting using ChatGPT."""
    try:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=f"Improve the formatting of this text without changing its meaning:\n\n{text}",
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        return f"Error with OpenAI API: {e}"

def get_modified_ics():
    """Fetch and modify ICS feed content."""
    try:
        response = requests.get(ICS_SOURCE_URL)
        response.raise_for_status()
        content = response.text
        lines = content.splitlines()
        new_lines = []

        for line in lines:
            if line.startswith("DESCRIPTION:"):
                description_content = line[len("DESCRIPTION:"):]
                improved_description = improve_text_with_chatgpt(description_content)
                new_lines.append(f"DESCRIPTION:{improved_description}")
            else:
                new_lines.append(line)

        return "\n".join(new_lines)

    except requests.exceptions.RequestException as e:
        return f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:ERROR\nDESCRIPTION:Failed to fetch ICS feed: {e}\nEND:VCALENDAR"

@app.route("/custom-feed.ics")
def serve_ics_feed():
    """Serve the modified ICS feed."""
    modified_ics = get_modified_ics()
    return Response(modified_ics, mimetype='text/calendar')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
