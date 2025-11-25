import time
from google import genai
from google.api_core.exceptions import ServiceUnavailable
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def gemini_request(text, attempts=3, wait_time=2):
    for attempt in range(1, attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=text
            )
            return response.text.strip()

        except ServiceUnavailable:
            if attempt == attempts:
                raise  # No more retries left

            print(f"[Attempt {attempt}/{attempts}] Model unavailable. Retrying in {wait_time}s...")
            time.sleep(wait_time)

        except Exception:
            # Any other error should not be retried
            raise

if __name__ == "__main__":
    prompt = "Write a short poem about the sea."
    print(gemini_request(prompt))