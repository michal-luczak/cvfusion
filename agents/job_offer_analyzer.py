import google.generativeai as genai
import json
import concurrent.futures
import re

SYSTEM_PROMPT = (
    "Jesteś ekspertem HR. Analizujesz ogłoszenia o pracę. "
    "Zwróć odpowiedź w formacie JSON z polami: "
    "requirements, technologies, soft_skills, experience_level, tone, keywords."
)

def extract_json_from_response(text: str) -> dict:
    """
    Usuwa markdown (np. ```json) i zwraca czysty JSON jako dict.
    """
    try:
        # Wyciągnij tylko fragment JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return {"error": "Nie znaleziono poprawnego JSON-a w odpowiedzi."}
    except json.JSONDecodeError as e:
        return {"error": f"Błąd dekodowania JSON: {str(e)}"}

class JobOfferAnalyzerAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def analyze(self, job_offer_text: str) -> dict:
        prompt = f"{SYSTEM_PROMPT}\n\n{job_offer_text}"
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self.model.generate_content, prompt)
                response = future.result(timeout=20)  # Timeout after 20s
            print(response.text)
            return extract_json_from_response(response.text)
        except concurrent.futures.TimeoutError:
            return {"error": "Przekroczono limit czasu oczekiwania na odpowiedź od Gemini."}
        except Exception as e:
            return {"error": str(e)}
