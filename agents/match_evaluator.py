import google.generativeai as genai
import json
import re

SYSTEM_PROMPT = (
    "Jesteś ekspertem HR. Oceniasz dopasowanie kandydata do oferty pracy na podstawie dwóch JSONów: "
    "1) job_offer (requirements, technologies, soft_skills, experience_level, tone, keywords), "
    "2) resume (experience, technologies, hard_skills, soft_skills). "
    "Zwróć JSON: score (0-100), missing_keywords, recommendation."
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

class MatchEvaluatorAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def evaluate(self, resume_json: dict, job_offer_json: dict) -> dict:

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"job_offer: {json.dumps(job_offer_json, ensure_ascii=False)}\n"
            f"resume: {json.dumps(resume_json, ensure_ascii=False)}"
        )
        print(3.5)
        print(prompt)
        try:
            response = self.model.generate_content(prompt)
            print(response.text)
            return extract_json_from_response(response.text)
        except json.JSONDecodeError:
            print(response.text)
            return {"error": "Nie udało się sparsować odpowiedzi LLM."}
        except Exception as e:
            return {"error": str(e)}
