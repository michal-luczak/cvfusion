import google.generativeai as genai
import json
import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Jesteś ekspertem HR. Oceniasz dopasowanie kandydata do oferty pracy na podstawie: "
    "1) Opisu oferty pracy (wymagania, technologie, umiejętności miękkie, poziom doświadczenia) "
    "2) Profilu kandydata (doświadczenie, technologie, umiejętności twarde i miękkie) "
    "Zwróć JSON: score (0-100), missing_skills, recommendation."
)

class JobMatchEvaluator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")
    
    def _extract_job_details(self, url: str) -> dict:
        """Pobiera i przetwarza ofertę pracy z LinkedIn/Pracuj.pl"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Usuń niepotrzebne elementy (dostosuj selektory dla LinkedIn/Pracuj.pl)
            for element in soup(["script", "style", "nav", "footer", "aside"]):
                element.decompose()
                
            # Ekstrakcja głównej treści (dostosuj dla konkretnej strony)
            job_content = soup.find('main') or soup.find('div', class_=re.compile('job-description|content'))
            job_text = job_content.get_text(separator="\n", strip=True) if job_content else ""
            
            return {
                "url": url,
                "content": job_text[:10000]  # Ogranicz do 10k znaków
            }
            
        except requests.RequestException as e:
            logger.warning(f"Błąd pobierania {url}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Nieoczekiwany błąd przetwarzania {url}: {e}")
            return None
    
    def _extract_response_text(self, response: str) -> str:
        """Wyciąga JSON z odpowiedzi modelu"""
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            return match.group() if match else None
        except Exception as e:
            logger.warning(f"Błąd ekstrakcji odpowiedzi: {e}")
            return None
    
    def evaluate_match(self, candidate_profile: dict, job_urls: list) -> list:
        """Ocenia dopasowanie kandydata do listy ofert pracy"""
        results = []
        
        for url in job_urls:
            try:
                # Pobierz szczegóły oferty pracy
                job_details = self._extract_job_details(url)
                if not job_details or not job_details.get("content"):
                    continue
                
                # Przygotuj prompt dla modelu
                prompt = f"""
                {SYSTEM_PROMPT}
                
                PROFIL KANDYDATA:
                {json.dumps(candidate_profile, ensure_ascii=False)}
                
                OFERTA PRACY (źródło: {url}):
                {job_details['content']}
                
                Format odpowiedzi (JSON):
                {{
                    "score": 0-100,
                    "missing_skills": [],
                    "recommendation": "",
                    "source": "{url}"
                }}
                """
                
                # Wywołaj model
                response = self.model.generate_content(prompt)
                extracted = self._extract_response_text(response.text)
                
                if not extracted:
                    continue
                    
                result = json.loads(extracted)
                result["source"] = url  # Dodaj URL oferty
                results.append(result)
                
            except json.JSONDecodeError:
                logger.warning(f"Nie można przetworzyć odpowiedzi JSON dla {url}")
                continue
            except Exception as e:
                logger.warning(f"Nieoczekiwany błąd dla {url}: {e}")
                continue
        
        # Posortuj wyniki od najlepszego dopasowania
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
