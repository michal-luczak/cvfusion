import os
import json
import google.generativeai as genai

SYSTEM_PROMPT = (
    "Jesteś ekspertem HR i copywriterem. Na podstawie danych z CV, oferty pracy oraz listy braków i zaleceń, generujesz nową wersję CV dopasowaną do oferty. "
    "Opcjonalnie generujesz list motywacyjny. Styl (formalny/nieformalny) jest parametryzowany. "
    "Zwróć odpowiedź w formacie JSON z polami: new_cv (tekst nowego CV), cover_letter (list motywacyjny, opcjonalnie). "
    "Odpowiadaj tylko JSON."
)

class ContentGeneratorAgent:
    """Generuje nową wersję CV dopasowaną do oferty oraz opcjonalnie list motywacyjny (z Gemini)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def generate(self, resume_json: dict, job_offer_json: dict, missing: list, recommendation: str, style: str = "formalny") -> dict:
        user_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"job_offer: {json.dumps(job_offer_json, ensure_ascii=False)}\n"
            f"resume: {json.dumps(resume_json, ensure_ascii=False)}\n"
            f"missing: {json.dumps(missing, ensure_ascii=False)}\n"
            f"recommendation: {recommendation}\n"
            f"style: {style}"
        )

        try:
            response = self.model.generate_content(user_prompt)
            print(response.text)
            return json.loads(response.text)
        except json.JSONDecodeError:
            print(response.text)
            return {"error": "Nie udało się sparsować odpowiedzi LLM (JSON)."}
        except Exception as e:
            return {"error": f"Wystąpił błąd: {str(e)}"}
