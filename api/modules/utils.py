from google import genai
from dotenv import load_dotenv
load_dotenv()


client = genai.Client()
def gemini_request(text):
    response= client.models.generate_content(
    model="gemini-2.5-flash",   
    contents=text
    )
    return response.text.strip()