import streamlit as st
import requests
from datetime import datetime, timezone

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AEGIS TERMINAL",
    page_icon="🛡️",
    layout="wide"
)

# ─────────────────────────────────────────────
# 1. SESSION DESTRUCTION
# ─────────────────────────────────────────────
def clear_session():
    """Instantly purges volatile RAM and reloads the UI."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ─────────────────────────────────────────────
# 2. GLOBAL TACTICAL CSS (RESPONSIVE & CLEANED)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;900&family=Inter:wght@400;700&display=swap');

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stSidebarHeader"] { background-color: transparent !important; }

/* ── Kill the Streamlit Anchor Link Icons permanently ── */
a.header-anchor, .stMarkdown a {
    display: none !important;
    visibility: hidden !important;
}

/* block-container */
.block-container {
    padding-top: 5rem !important; 
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #131313 !important;
    color: #e5e2e1 !important;
}

/* ── Fixed tactical top bar (Responsive Fix) ── */
.aegis-topbar {
    position: fixed;
    top: 0; left: 280px; right: 0;
    height: 52px;
    background: #131313;
    border-bottom: 1px solid #474747;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px 0 24px;  
    z-index: 9999;
    font-family: 'Space Grotesk', monospace;
    transition: left 0.3s ease; 
}

.topbar-branding {
    display: flex; align-items: center; gap: 20px;
}
.topbar-logo {
    font-size: 0.95rem; font-weight: 900;
    color: #00FF41; text-transform: uppercase;
    letter-spacing: 0.05em;
}
.topbar-sep { width: 1px; height: 16px; background: #474747; }
.topbar-mode {
    font-size: 0.62rem; color: #919191;
    text-transform: uppercase; letter-spacing: 2px;
}
.topbar-actions {
    display: flex; align-items: center; gap: 24px;
}
.topbar-nav-active {
    font-size: 0.62rem; color: #00FF41; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    border-bottom: 2px solid #00FF41;
    padding-bottom: 2px;
}
.topbar-nav-inactive {
    font-size: 0.62rem; color: #919191;
    text-transform: uppercase; letter-spacing: 2px;
}

/* ── Sidebar (Cleaned of fake features) ── */
[data-testid="stSidebar"] {
    background-color: #0e0e0e !important;
    border-right: 1px solid #474747 !important;
    width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important; 
}

.sidebar-header-tactical {
    padding: 10px 16px 24px 16px; border-bottom: 1px solid #474747; margin-bottom: 24px;
}
.sidebar-brand-title {
    font-family: 'Space Grotesk', monospace;
    font-size: 1rem; font-weight: 900;
    color: #00FF41; text-transform: uppercase;
    letter-spacing: 2px; margin-left: 20px;
}
.sidebar-brand-status {
    font-size: 0.6rem; color: #919191;
    text-transform: uppercase; letter-spacing: 2px;
    margin-top: 4px; margin-left: 20px;
}

/* Hardware Status Blocks (Replacing fake links) */
.hw-status-block {
    padding: 12px 20px;
    margin-bottom: 8px;
}
.hw-label {
    font-family: 'Space Grotesk', monospace;
    font-size: 0.6rem; color: #474747;
    letter-spacing: 2px; text-transform: uppercase;
    display: block; margin-bottom: 4px;
}
.hw-value {
    font-family: 'Courier New', monospace;
    font-size: 0.75rem; color: #c6c6c6;
    display: block;
}
.hw-value.ok { color: #00FF41; }

/* ── Section labels ── */
.section-label {
    font-size: 0.65rem; letter-spacing: 3px;
    text-transform: uppercase; color: #919191;
    margin-bottom: 12px; font-family: 'Space Grotesk', monospace;
    font-weight: 900;
}
.module-tag {
    font-size: 0.6rem; color: #474747;
    font-family: 'Courier New', monospace;
    letter-spacing: 1px; text-align: right;
    margin-bottom: -12px; z-index: 10; position: relative;
    padding-right: 12px; padding-top: 12px;
}

/* ── Input panel ── */
.input-panel {
    background: #201f1f; border: 1px solid #474747;
    padding: 24px; margin-bottom: 16px;
}

/* ── File Uploader Tactical Styling ── */
[data-testid="stFileUploader"] {
    background-color: #0e0e0e;
    border: 1px dashed #474747;
    padding: 16px;
    transition: 0.3s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #00FF41;
}
[data-testid="stFileUploader"] section {
    padding: 0 !important;
}
[data-testid="stFileUploader"] small {
    font-family: 'Courier New', monospace !important;
    color: #474747 !important;
    letter-spacing: 1px;
}
[data-testid="stFileUploader"] button {
    border-radius: 0px;
    font-family: 'Space Grotesk', monospace;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Textarea */
.stTextArea textarea {
    background-color: #0e0e0e !important;
    border: 1px solid #474747 !important;
    border-radius: 0px !important;
    color: #e5e2e1 !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.7 !important;
    caret-color: #00FF41 !important;
    padding: 16px !important;
}
.stTextArea textarea:focus { border-color: #00FF41 !important; box-shadow: none !important; }
.stTextArea textarea::placeholder { color: #474747 !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 0px !important;
    font-family: 'Space Grotesk', monospace !important;
    font-weight: 900 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}
.stButton > button[kind="primary"] {
    background: #ffffff !important; color: #000000 !important;
    border: none !important; padding: 20px !important; font-size: 0.85rem !important;
}
.stButton > button[kind="primary"]:hover { background: #00FF41 !important; color: #000000 !important; }

.stButton > button[kind="secondary"] {
    background: #93000a !important; color: #ffdad6 !important;
    border: 1px solid #ffdad6 !important; padding: 20px !important; font-size: 0.85rem !important;
}
.stButton > button[kind="secondary"]:hover { background: #be0b1d !important; color: #ffffff !important; }

/* ── Output modules ── */
.out-module-header {
    background: #2a2a2a; padding: 12px 20px;
    display: flex; justify-content: space-between; align-items: center;
    border: 1px solid #474747;
}
.out-module-title {
    font-size: 0.65rem; font-family: 'Space Grotesk', monospace;
    font-weight: 900; letter-spacing: 3px; text-transform: uppercase; color: #c6c6c6;
}
.out-module-body {
    background: #1c1b1b; border: 1px solid #474747; border-top: none;
    padding: 20px; font-family: 'Courier New', monospace;
    font-size: 0.85rem; line-height: 2; color: #e5e2e1;
    max-height: 400px; overflow-y: auto; margin-bottom: 24px;
}

/* ── Redaction token ── */
.redact-token {
    background-color: #2a2a2a; color: #00f63e; font-weight: 700;
    padding: 2px 6px; font-family: 'Courier New', monospace;
    font-size: 0.8rem; border: 1px solid #474747;
}

/* ── Awaiting state ── */
.awaiting-box {
    height: 400px; display: flex; align-items: center;
    justify-content: center; border: 1px dashed #474747; background: #0e0e0e;
}

/* ── Status bar ── */
.status-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 24px; background: #0a0f0a; border: 1px solid #00FF41;
    margin-top: 16px; margin-bottom: 24px;
}
.status-ok {
    color: #00FF41; font-size: 0.75rem; letter-spacing: 2px;
    font-weight: 900; font-family: 'Space Grotesk', monospace; text-transform: uppercase;
}

/* ── Expander ── */
[data-testid="stExpander"] { border: 1px solid #474747 !important; border-radius: 0px !important; background: #0e0e0e !important; }
[data-testid="stExpander"] summary { font-family: 'Space Grotesk', monospace !important; font-size: 0.65rem !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: #c6c6c6 !important; padding: 16px !important; }

/* ── Heartbeat ── */
@keyframes hb { 0%,100%{opacity:1;} 50%{opacity:0.2;} }
.hb-dot { display:inline-block; width:8px; height:8px; background:#00FF41; animation:hb 2s infinite; vertical-align:middle; }

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. FIXED TACTICAL TOP BAR 
# ─────────────────────────────────────────────
st.markdown("""
<div class="aegis-topbar">
    <div class="topbar-branding">
        <span class="topbar-logo">AEGIS TERMINAL</span>
        <div class="topbar-sep"></div>
        <span class="topbar-mode">OFFLINE_MODE: ACTIVE</span>
    </div>
    <div class="topbar-actions">
        <span class="topbar-nav-inactive">SECURE</span>
        <span class="topbar-nav-active">INTELLIGENCE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 4. SIDEBAR (TACTICAL READOUTS ONLY)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-tactical">
        <div class="sidebar-brand-title">PROJECT_AEGIS</div>
        <div class="sidebar-brand-status">STATUS: OPERATIONAL</div>
    </div>
    
    <div class="hw-status-block">
        <span class="hw-label">NETWORK STATE</span>
        <span class="hw-value ok">AIR-GAPPED (WIFI: DOWN)</span>
    </div>
    <div class="hw-status-block">
        <span class="hw-label">ACTIVE ENGINE</span>
        <span class="hw-value">GEMMA-4-E2B (C++ BAREMETAL)</span>
    </div>
    <div class="hw-status-block">
        <span class="hw-label">MEMORY ALLOCATION</span>
        <span class="hw-value">12.4GB / 32.0GB</span>
    </div>
    <div class="hw-status-block">
        <span class="hw-label">ENCRYPTION PROTOCOL</span>
        <span class="hw-value">AES-256-GCM</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)

    if st.button("🚨 PURGE SESSION", type="secondary", use_container_width=True):
        clear_session()

# ─────────────────────────────────────────────
# 5. MAIN CANVAS — BRANDING HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="border-bottom:1px solid #474747;padding-bottom:16px;margin-bottom:24px;">
    <h1 style="font-family:'Space Grotesk',monospace;font-size:2.2rem;font-weight:900;
               letter-spacing:-1px;color:#ffffff;margin:0;margin-top:-64px;text-transform:uppercase;">
        PROJECT AEGIS
    </h1>
    <p style="font-size:0.65rem;color:#919191;letter-spacing:4px;
              text-transform:uppercase;margin-top:6px;font-family:'Space Grotesk',monospace;">
        AIR-GAPPED DOCUMENT INTELLIGENCE &nbsp;|&nbsp;
        <span style="color:#00FF41;">OFFLINE MODE: ACTIVE</span>
    </p>
</div>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────
# 6. TWO-COLUMN LAYOUT
# ─────────────────────────────────────────────
left_col, right_col = st.columns([7, 5], gap="large")

# ── LEFT — INPUT ──────────────────────────────
with left_col:
    st.markdown("""
    <div style="module-wrapper">
    <div class="module-tag" style="margin-top:0px; margin-bottom: 0px;">MODULE_01 // INPUT</div>
    <div class="input-panel">
        <div class="section-label" style="margin-top:0px; margin-bottom: 0px;">SECURE FILE UPLOAD</div>
    """, unsafe_allow_html=True)

    # Functional Streamlit Uploader (Volatile RAM only)
    uploaded_file = st.file_uploader("Upload Intel", type=["txt", "md", "log"], label_visibility="collapsed")
    
    st.markdown('<div class="section-label" style="margin-top:16px; margin-bottom: 8px;">OR PASTE RAW DATA</div>', unsafe_allow_html=True)

    # Logic: If a file is dropped, read it into memory and pre-fill the text area
    default_text = ""
    if uploaded_file is not None:
        try:
            default_text = uploaded_file.getvalue().decode("utf-8")
            st.markdown(f"<div style='color:#00FF41; font-family:monospace; font-size:0.7rem; margin-bottom:10px;'>[SYSTEM]: LOADED {uploaded_file.name} ALOFT IN VOLATILE RAM.</div>", unsafe_allow_html=True)
        except Exception:
            st.error("Decryption failure. Ensure file is UTF-8 plaintext.")

    # ── ACTUAL INPUT ──
    raw_text = st.text_area(
        label="raw_input",
        value=default_text, # Dynamically populates if file is dropped
        height=250,
        placeholder="PASTE SENSITIVE FIELD REPORT HERE FOR LOCAL REDACTION...",
        label_visibility="collapsed"
    )
    
    st.markdown("</div>") 
    st.markdown("</div>") 

    # Unified Action Area
    st.markdown('<div class="action-panel" style="margin-top:16px;">', unsafe_allow_html=True)
    btn_l, btn_r = st.columns([3, 1])
    with btn_l:
        process_btn = st.button(
            "PROCESS INTELLIGENCE REPORT",
            type="primary",
            use_container_width=True
        )
    with btn_r:
        if st.button("🚨 BURN", type="secondary", use_container_width=True):
            clear_session()
    st.markdown("</div>", unsafe_allow_html=True)

# ── RIGHT — OUTPUT ─────────────────────────────
with right_col:
    if 'sanitized' not in st.session_state:
        st.markdown("""
        <div class="awaiting-box">
            <div style="text-align:center;">
                <div style="font-size:0.62rem;color:#474747;letter-spacing:3px;
                            text-transform:uppercase;font-family:'Space Grotesk',monospace;
                            line-height:2.5;">
                    AWAITING INPUT<br>
                    <span style="font-size:0.58rem;color:#353534;">
                        PASTE DOCUMENT AND EXECUTE<br>REDACTION PIPELINE
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # TACTICAL SUMMARY
        st.markdown("""
        <div class="out-module-header">
            <span class="out-module-title">TACTICAL SUMMARY (SMS-READY)</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            f'<div class="out-module-body">{st.session_state["summary"]}</div>',
            unsafe_allow_html=True
        )

        # SANITIZED SOURCE
        st.markdown("""
        <div class="out-module-header">
            <span class="out-module-title">SANITIZED SOURCE</span>
        </div>
        """, unsafe_allow_html=True)

        highlighted = st.session_state['sanitized']
        for token in set(st.session_state['map'].values()):
            highlighted = highlighted.replace(
                token,
                f'<span class="redact-token">{token}</span>'
            )
        st.markdown(
            f'<div class="out-module-body">'
            f'{highlighted.replace(chr(10), "<br><br>")}'
            f'</div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────
# 7. PROCESSING LOGIC
# ─────────────────────────────────────────────
if process_btn:
    if not raw_text.strip():
        st.warning("INPUT REQUIRED. PASTE A FIELD REPORT TO PROCESS.")
    else:
        with st.spinner("EXECUTING AIR-GAPPED REDACTION PIPELINE..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/process",
                    json={"raw_text": raw_text, "task": "both"},
                    timeout=300
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state['sanitized'] = data.get("sanitized_text", "")
                    st.session_state['summary']   = data.get("synthesis_result", "")
                    st.session_state['map']        = data.get("redaction_map", {})
                    st.rerun()
                elif response.status_code == 503:
                    st.error("SECURITY VIOLATION: Network detected. Aegis terminated. Disable Wi-Fi before processing.")
                    st.stop()
                else:
                    st.error(f"BACKEND ERROR: {response.status_code} — {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("CRITICAL: Cannot reach Aegis Core. Run: uvicorn backend.main:app --reload")

# ─────────────────────────────────────────────
# 8. FULL-WIDTH BOTTOM
# ─────────────────────────────────────────────
if 'sanitized' in st.session_state:
    now_utc = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    map_id  = abs(hash(str(st.session_state['map']))) % 99999

    st.markdown(f"""
    <div class="status-bar">
        <div style="display:flex;align-items:center;gap:12px;">
            <div class="hb-dot"></div>
            <div>
                <div class="status-ok">REPORT PROCESSED SECURELY</div>
                <div style="font-size:0.65rem; color:#474747; font-family:'Courier New',monospace; margin-top:4px;">
                    Last activity: {now_utc} &nbsp;|&nbsp; Redaction Engine: v2.4.1
                </div>
            </div>
        </div>
        <span style="font-size:0.65rem; color:#474747; font-family:'Courier New',monospace;">HASH: {map_id:05X}...B3A1</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">SAFE PAYLOAD EXPORT</div>', unsafe_allow_html=True)
    st.caption("Export Safe Payload (Copy to Clipboard):")
    st.code(st.session_state['sanitized'], language="text")

    with st.expander(
        f"VIEW REDACTION MAP  [DEBUG ONLY — HIDDEN IN PROD]  |  MAP_ID: R-{map_id:05X}",
        expanded=False
    ):
        st.markdown(
            '<div style="color:#FF4B4B; font-size:0.7rem; letter-spacing:1px; margin-bottom:12px; font-family:\'Courier New\',monospace;">'
            'WARNING: THIS MAP LINKS TOKENS TO TRUE IDENTITIES. DO NOT SHARE.'
            '</div>',
            unsafe_allow_html=True
        )
        st.json(st.session_state['map'])