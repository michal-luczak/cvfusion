import streamlit as st
from agents.job_offer_analyzer import JobOfferAnalyzerAgent
from agents.resume_parser import ResumeParserAgent
from agents.match_evaluator import MatchEvaluatorAgent

st.set_page_config(page_title="SmartApply", layout="centered")
st.title("SmartApply – Dopasowanie CV do oferty pracy")

st.markdown("Wklej ogłoszenie i swoje CV. Kliknij **Analizuj**, aby sprawdzić dopasowanie.")

api_key = st.text_input("🔐 Wklej swój Google Gemini API Key:", type="password")
job_offer_text = st.text_area("📄 Treść ogłoszenia o pracę", height=200)
resume_text = st.text_area("📄 Treść CV", height=200)

if st.button("Analizuj"):
    if not api_key:
        st.error("Wymagany jest klucz API.")
    else:
        with st.spinner("Analizuję dane..."):
            job_agent = JobOfferAnalyzerAgent(api_key)
            resume_agent = ResumeParserAgent(api_key)
            match_agent = MatchEvaluatorAgent(api_key)

            print(1)
            
            job_offer_json = job_agent.analyze(job_offer_text)
            print(2)
            resume_json = resume_agent.parse(resume_text)
            print(3)
            result = match_agent.evaluate(resume_json, job_offer_json)
            print(4)

        st.subheader("📊 Wyniki analizy:")
        if "error" in result:
            st.error(result["error"])
        else:
            st.metric("Scoring dopasowania", f"{result.get('score', 0)}%")
            st.write("**🔎 Brakujące słowa kluczowe:**", result.get("missing_keywords", []))
            st.write("**💡 Rekomendacje:**", result.get("recommendation", "-"))
