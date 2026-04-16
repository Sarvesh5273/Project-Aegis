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
                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/process",
                    json={"raw_text": raw_text, "task": "both"}
                )
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Report Processed Securely.")
                    
                    # 1. Synthesized Intelligence Brief
                    st.subheader("Tactical Summary")
                    st.info(data.get("synthesis_result", ""))

                    # 2. Real-Time Redaction Visualizer (UI Polish)
                    st.subheader("Sanitized Source")
                    sanitized_text = data.get("sanitized_text", "")
                    redaction_map = data.get("redaction_map", {})
                    
                    visual_text = sanitized_text
                    # Inject HTML spans to highlight redactions dynamically
                    for original, token in redaction_map.items():
                        visual_text = visual_text.replace(
                            token, 
                            f'<span style="background-color:#ff4444;color:white;padding:2px 4px;border-radius:3px;font-weight:bold;">{token}</span>'
                        )
                    st.markdown(visual_text, unsafe_allow_html=True)
                    
                    with st.expander("View Redaction Map"):
                        st.json(redaction_map)
                else:
                    st.error(f"Backend Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("CRITICAL: Cannot connect to Aegis Core. Is the backend running?")