from google import genai
from dotenv import load_dotenv
load_dotenv()


client = genai.Client()
def gemini_request(text):
    try:
        # First attempt with the lite model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=text
        )
        return response.text.strip()

    except Exception as e:
        print(f"Lite model failed with error: {e}")
        # Retry using the full flash model
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=text
        )
        return response.text.strip()


if __name__=="__main__":
    test_prompt="Write a short poem about the sea."
    print(gemini_request(test_prompt))