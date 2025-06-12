import streamlit as st
from agents.job_offer_analyzer import JobOfferAnalyzerAgent
from agents.resume_parser import ResumeParserAgent
from agents.match_evaluator import MatchEvaluatorAgent
import PyPDF2
import io

st.set_page_config(page_title="SmartApply", layout="centered")
st.title("SmartApply – Dopasowanie CV do oferty pracy")

st.markdown("Wklej ogłoszenie i załaduj swoje CV w formacie PDF. Kliknij **Analizuj**, aby sprawdzić dopasowanie.")

api_key = st.text_input("🔐 Wklej swój Google Gemini API Key:", type="password")
job_offer_text = st.text_area("📄 Treść ogłoszenia o pracę", height=200)
resume_file = st.file_uploader("📄 Załaduj swoje CV (PDF)", type=["pdf"])

if st.button("Analizuj"):
    if not api_key:
        st.error("Wymagany jest klucz API.")
    elif not resume_file:
        st.error("Proszę załączyć plik CV w formacie PDF.")
    else:
        with st.spinner("Analizuję dane..."):
            # Odczytaj tekst z PDF
            pdf_reader = PyPDF2.PdfReader(resume_file)
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
            
            job_agent = JobOfferAnalyzerAgent(api_key)
            resume_agent = ResumeParserAgent(api_key)
            match_agent = MatchEvaluatorAgent(api_key)

            job_offer_json = job_agent.analyze(job_offer_text)
            resume_json = resume_agent.parse(resume_text)
            result = match_agent.evaluate(resume_json, job_offer_json)

        st.subheader("📊 Wyniki analizy:")
        if "error" in result:
            st.error(result["error"])
        else:
            st.metric("Scoring dopasowania", f"{result.get('score', 0)}%")
            st.write("**🔎 Brakujące słowa kluczowe:**", result.get("missing_keywords", []))
            st.write("**💡 Rekomendacje:**", result.get("recommendation", "-"))