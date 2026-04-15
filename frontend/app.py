import streamlit as st
import requests

st.set_page_config(page_title="Project Aegis", page_icon="🛡️", layout="centered")

st.title("🛡️ Project Aegis")
st.caption("Air-Gapped Document Intelligence | Offline Mode: ACTIVE")

raw_text = st.text_area("Secure Input", height=200, placeholder="Paste intercepted document here...")


if st.button("Process Intelligence Report", type="primary"):
    if not raw_text.strip():
        st.warning("Input required.")
    else:
        with st.spinner("Enforcing air-gap... sanitizing and synthesizing locally..."):
            try:
                # Request BOTH tasks from the backend
                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/process",
                    json={"raw_text": raw_text, "task": "both"}
                )
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Report Processed Securely.")
                    
                    # Display the Synthesized Intelligence Brief
                    st.subheader("Tactical Summary")
                    st.info(data.get("synthesis_result", ""))

                    # Display the sanitized text
                    st.subheader("Sanitized Source")
                    st.write(data.get("sanitized_text", ""))
                    
                    with st.expander("View Redaction Map"):
                        st.json(data.get("redaction_map", {}))
                else:
                    st.error(f"Backend Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("CRITICAL: Cannot connect to Aegis Core. Is the backend running?")