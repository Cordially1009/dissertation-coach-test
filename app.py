import streamlit as st
import datetime
from google import genai
from google.genai import types

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Project SEAN — Systematic Evaluation & Alignment Navigator",
    page_icon="🎓",
    layout="wide",
)

# ---------------------------------------------------------
# Secrets & API Initialization
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("Please provide a Gemini API Key in Streamlit Secrets or via the sidebar to continue.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing Google GenAI Client: {e}")
    st.stop()

# ---------------------------------------------------------
# Master Grounding System Prompt
# ---------------------------------------------------------
SYSTEM_PROMPT = """You are Project SEAN (Systematic Evaluation & Alignment Navigator), an expert academic research design coach auditing graduate research proposals grounded in Creswell & Creswell and Terrell.

CORE MISSION:
Audit methodological alignment between the Problem Statement, Purpose Statement, and Research Questions. Cultivate scholarly agency and critical thinking through structured Socratic interrogation.

ABSOLUTE GUARDRAILS:
1. ANTI-GHOSTWRITING: Never draft, rewrite, complete, or provide sentence templates for the candidate's topic. Never offer "suggested phrasing" in finished prose.
2. DOMAIN-DISJOINT EXEMPLARS: If the candidate asks for an example, you MUST use an entirely unrelated discipline (e.g., deep-sea marine biology, Renaissance architecture, astrophysics). Explicitly state that the example comes from an unrelated field to illustrate structural logic without completing their thinking.
3. THREE-TIER GRADUATED SCAFFOLDING (When the student is stuck):
   - Tier 1 (Probe): Name the conceptual tension and ask them to reflect on it.
   - Tier 2 (Theoretical Context): Explain the underlying Creswell/Terrell rule.
   - Tier 3 (Functional Choice Menu): Provide an abstract menu of research intents, requiring the student to assemble their own draft.

MANDATORY AUDIT LAYOUT:
Every diagnostic review must strictly follow this 3-part layout:
1. **Observation**: Concisely identify the submitted elements (stated paradigm, core constructs, target population, and setting).
2. **Critique**: Diagnose methodological congruence using Creswell/Terrell principles (e.g., construct granularity, elimination of causal language in qualitative designs, operational definitions in quantitative designs).
3. **Systematic Prompt**: Deliver one targeted Socratic prompt requiring the student to revise their own wording.

TONE:
Collegial, academically rigorous, direct, and unpadded. Eliminate generic praise or sycophancy ("Great topic!"). Open immediately with the observation and critique."""

# ---------------------------------------------------------
# State Management Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "problem" not in st.session_state:
    st.session_state.problem = ""
if "purpose" not in st.session_state:
    st.session_state.purpose = ""
if "rq" not in st.session_state:
    st.session_state.rq = ""

# Callback to sync text areas with session state
def update_drafts():
    st.session_state.problem = st.session_state._problem
    st.session_state.purpose = st.session_state._purpose
    st.session_state.rq = st.session_state._rq

# ---------------------------------------------------------
# Sidebar: Methodological Configuration & Tools
# ---------------------------------------------------------
with st.sidebar:
    st.title("🧭 Configuration")
    
    methodology_track = st.radio(
        "Methodological Track",
        ["Qualitative", "Quantitative", "Mixed Methods"],
        index=0,
    )
    
    tradition_options = {
        "Qualitative": ["Phenomenology", "Case Study", "Grounded Theory", "Ethnography", "Narrative Inquiry"],
        "Quantitative": ["Experimental", "Quasi-Experimental", "Correlational", "Descriptive / Survey"],
        "Mixed Methods": ["Convergent Parallel", "Explanatory Sequential", "Exploratory Sequential"]
    }
    
    selected_tradition = st.selectbox("Design / Tradition", tradition_options[methodology_track])
    
    st.markdown("---")
    st.markdown("### Session Tools")
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.problem = ""
        st.session_state.purpose = ""
        st.session_state.rq = ""
        st.rerun()

# ---------------------------------------------------------
# Main Viewport: Header & Workspace
# ---------------------------------------------------------
st.title("🎓 Project SEAN")
st.markdown("##### Systematic Evaluation & Alignment Navigator | Problem, Purpose & Research Questions Alignment")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("#### 📋 Methodological Alignment Workspace")
col1, col2, col3 = st.columns(3)

with col1:
    st.text_area("1. Problem Statement (The Gap)", value=st.session_state.problem, height=200, key="_problem", on_change=update_drafts)
with col2:
    st.text_area("2. Purpose Statement (The Intent)", value=st.session_state.purpose, height=200, key="_purpose", on_change=update_drafts)
with col3:
    st.text_area("3. Research Question(s) (The Inquiry)", value=st.session_state.rq, height=200, key="_rq", on_change=update_drafts)

# Conditional Routing & Status Badge
active_count = sum(1 for text in [st.session_state.problem, st.session_state.purpose, st.session_state.rq] if text.strip())

if active_count == 0:
    st.info("✅ **Status:** Ready for Ideation / Exploratory Conceptual Questions")
    audit_scope = "IDEATION: The student is exploring ideas. Act as a conceptual boundary-setter."
elif active_count == 1:
    st.warning("⚠️ **Status:** Isolated Element Audit (1 of 3 Elements Populated)")
    audit_scope = "ISOLATED_ELEMENT: Audit the single element for construct precision. Prompt them toward the next logical piece."
elif active_count == 2:
    st.warning("⚠️ **Status:** Partial Alignment Audit (2 of 3 Elements Populated)")
    audit_scope = "PARTIAL_ALIGNMENT: Audit the internal consistency between the two provided elements."
else:
    st.success("✅ **Status:** Ready for Complete Alignment Audit (All 3 Elements Populated)")
    audit_scope = "FULL_ALIGNMENT: Conduct a complete triadic audit evaluating the structural chain: Problem <-> Purpose <-> Research Questions."

# ---------------------------------------------------------
# Action Buttons (Audit & Export)
# ---------------------------------------------------------
b_col1, b_col2 = st.columns([1, 1])

with b_col1:
    run_audit = st.button("🔍 Run Methodological Alignment Audit", type="primary", use_container_width=True)

with b_col2:
    # Prepare the Export Document dynamically
    export_text = f"# Project SEAN: Session Summary & Notes\n"
    export_text += f"**Date:** {datetime.datetime.now().strftime('%B %d, %Y - %H:%M')}\n"
    export_text += f"**Methodology:** {methodology_track} ({selected_tradition})\n\n"
    export_text += f"## 1. Problem Statement\n{st.session_state.problem if st.session_state.problem else '[Not drafted]'}\n\n"
    export_text += f"## 2. Purpose Statement\n{st.session_state.purpose if st.session_state.purpose else '[Not drafted]'}\n\n"
    export_text += f"## 3. Research Questions\n{st.session_state.rq if st.session_state.rq else '[Not drafted]'}\n\n"
    export_text += f"---\n## Latest Diagnostic Feedback\n\n"
    
    # Grab the last assistant message for the export notes
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            export_text += msg["content"]
            break

    st.download_button(
        label="📥 Export Summary & Session Notes",
        data=export_text,
        file_name="SEAN_Session_Notes.md",
        mime="text/markdown",
        use_container_width=True
    )

st.markdown("---")
st.markdown("### 💬 Socratic Dialogue & Feedback")

# Render existing chat history
for msg in st.session_state.messages:
    if msg["role"] != "system_hidden": # Hide the backend prompt from the UI
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---------------------------------------------------------
# Conversational Input & API Call
# ---------------------------------------------------------
chat_input = st.chat_input("Ask a clarifying question or test out a concept...")

if run_audit or chat_input:
    # 1. Construct the context-aware payload
    if run_audit:
        ui_display_message = "*(Triggered Methodological Alignment Audit)*"
        system_payload = f"""[AUDIT REQUEST]
Current Scope: {audit_scope}
Methodology: {methodology_track} ({selected_tradition})
Problem: {st.session_state.problem}
Purpose: {st.session_state.purpose}
RQ: {st.session_state.rq}"""
    else:
        ui_display_message = chat_input
        system_payload = f"""[USER QUESTION]: {chat_input}
Current Scope: {audit_scope}
Methodology: {methodology_track} ({selected_tradition})
Problem: {st.session_state.problem}
Purpose: {st.session_state.purpose}
RQ: {st.session_state.rq}"""

    # 2. Append to UI and Session State
    st.session_state.messages.append({"role": "user", "content": ui_display_message})
    with st.chat_message("user"):
        st.markdown(ui_display_message)

    # 3. Call Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_payload,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2, # Low temp to keep critiques rigid and academic
            ),
        )
        assistant_reply = response.text
    except Exception as e:
        assistant_reply = f"API Error: {e}"

    # 4. Save and display response
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)