import streamlit as st
from agents.job_offer_analyzer import JobOfferAnalyzerAgent
from agents.resume_parser import ResumeParserAgent
from agents.match_evaluator import JobMatchEvaluator
import PyPDF2
import io

st.set_page_config(page_title="SmartApply", layout="centered")
st.title("SmartApply – Dopasowanie CV do oferty pracy")

st.markdown("""
Wybierz źródło oferty pracy:
1. Wklej tekst ogłoszenia
2. Podaj link do oferty z LinkedIn/Pracuj.pl
""")

api_key = st.text_input("🔐 Wklej swój Google Gemini API Key:", type="password")

# Wybór trybu wprowadzania oferty pracy
input_mode = st.radio("Tryb wprowadzania oferty:", ["Tekst ogłoszenia", "Link do oferty"])

job_offer_text = None
job_url = None

if input_mode == "Tekst ogłoszenia":
    job_offer_text = st.text_area("📄 Treść ogłoszenia o pracę", height=200)
else:
    job_url = st.text_input("🔗 Wklej link do oferty (LinkedIn/Pracuj.pl)")
    if job_url:
        if not any(domain in job_url for domain in ["linkedin.com", "pracuj.pl"]):
            st.warning("Proszę podać link z LinkedIn lub Pracuj.pl")

resume_file = st.file_uploader("📄 Załaduj swoje CV (PDF)", type=["pdf"])

if st.button("Analizuj"):
    if not api_key:
        st.error("Wymagany jest klucz API.")
    elif not resume_file:
        st.error("Proszę załączyć plik CV w formacie PDF.")
    elif input_mode == "Tekst ogłoszenia" and not job_offer_text:
        st.error("Proszę wprowadzić treść ogłoszenia.")
    elif input_mode == "Link do oferty" and not job_url:
        st.error("Proszę wprowadzić link do oferty.")
    else:
        with st.spinner("Analizuję dane..."):
            try:
                # Odczytaj tekst z PDF
                pdf_reader = PyPDF2.PdfReader(resume_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                
                resume_agent = ResumeParserAgent(api_key)
                resume_json = resume_agent.parse(resume_text)

                if input_mode == "Tekst ogłoszenia":
                    # Tradycyjna analiza tekstu ogłoszenia
                    job_agent = JobOfferAnalyzerAgent(api_key)
                    job_offer_json = job_agent.analyze(job_offer_text)
                    
                    match_agent = MatchEvaluatorAgent(api_key)
                    result = match_agent.evaluate(resume_json, job_offer_json)
                else:
                    # Nowa funkcjonalność analizy linków
                    job_evaluator = JobMatchEvaluator(api_key)
                    candidate_profile = {
                        "experience": resume_json.get("experience", ""),
                        "technologies": resume_json.get("skills", []),
                        "hard_skills": resume_json.get("hard_skills", []),
                        "soft_skills": resume_json.get("soft_skills", []),
                        "experience_level": resume_json.get("experience_level", "")
                    }
                    
                    results = job_evaluator.evaluate_match(candidate_profile, [job_url])
                    if results:
                        result = results[0]  # Najlepsze dopasowanie
                    else:
                        result = {"error": "Nie udało się przeanalizować oferty pracy"}

                # Wyświetl wyniki
                st.subheader("📊 Wyniki analizy:")
                if "error" in result:
                    st.error(result["error"])
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Scoring dopasowania", f"{result.get('score', 0)}%")
                    with col2:
                        st.metric("Źródło", "LinkedIn" if "linkedin.com" in (job_url or "") else "Pracuj.pl" if job_url else "Tekst")
                    
                    st.write("---")
                    
                    with st.expander("🔍 Szczegółowe wyniki"):
                        st.write("**🔎 Brakujące umiejętności:**")
                        if result.get("missing_skills"):
                            for skill in result["missing_skills"]:
                                st.write(f"- {skill}")
                        else:
                            st.write("Brak znaczących braków")
                        
                        st.write("\n**💡 Rekomendacje:**")
                        st.write(result.get("recommendation", "-"))
                        
                        if job_url:
                            st.write("\n**🔗 Link do oferty:**")
                            st.write(job_url)

            except Exception as e:
                st.error(f"Wystąpił błąd podczas analizy: {str(e)}")