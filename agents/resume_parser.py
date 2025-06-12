import google.generativeai as genai
import json
import json
import re


SYSTEM_PROMPT = (
    "Jesteś ekspertem HR. Analizujesz CV kandydata. "
    "Zwróć odpowiedź w formacie JSON z polami: "
    "experience, technologies, hard_skills, soft_skills."
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


class ResumeParserAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def parse(self, resume_text: str) -> dict:
        try:
            response = self.model.generate_content(f"{SYSTEM_PROMPT}\n\n{resume_text}")
            print(response.text)
            return extract_json_from_response(response.text)
        except json.JSONDecodeError:
            print(response.text)
            return {"error": "Nie udało się sparsować odpowiedzi LLM."}
        except Exception as e:
            return {"error": str(e)}
