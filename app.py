import streamlit as st
import datetime
from google import genai
from google.genai import types

# ---------------------------------------------------------
# Page Configuration & Custom CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Project SEAN",
    page_icon="✦",
    layout="wide",
)

# Custom CSS to force a single-screen layout (preventing page scroll)
st.markdown("""
    <style>
        /* Hide the default Streamlit top header to buy more vertical space */
        [data-testid="stHeader"] {
            display: none;
        }
        .block-container {
            padding-top: 1rem; 
            padding-bottom: 1rem;
        }
        [data-testid="stSidebar"] {
            min-width: 300px;
            max-width: 300px;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-top: 0px;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 1.1rem;
            color: #555;
            margin-top: 5px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

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
SYSTEM_PROMPT = """You are Project SEAN, an expert academic research design coach auditing graduate research proposals.

CORE MISSION:
Audit methodological alignment between the Problem Statement, Purpose Statement, and Research Questions. Cultivate scholarly agency through structured Socratic interrogation. 
*Note: The user only selects a broad methodology (Qualitative/Quantitative/Mixed). Use Socratic dialogue to help them figure out their specific research tradition.*

ABSOLUTE GUARDRAILS:
1. ANTI-GHOSTWRITING: Never draft, rewrite, complete, or provide sentence templates for the candidate's topic. 
2. NO NAME-DROPPING: Do NOT mention Creswell, Terrell, or the names of specific textbooks in your responses. You must silently enforce their methodological principles without citing them to the user.
3. DOMAIN-DISJOINT EXEMPLARS: If the candidate asks for an example, use an entirely unrelated discipline (e.g., deep-sea marine biology, Renaissance architecture).
4. SUCCESS DIRECTIVE: When the student successfully revises a component and it demonstrates strong methodological alignment, praise the specific strength and EXPLICITLY instruct them to "copy your finalized [Problem/Purpose/Research Question] and paste it into the Workspace above" so it is ready for the final audit.

MANDATORY AUDIT LAYOUT:
Every diagnostic review must strictly follow this 3-part layout:
1. **Observation**: Concisely identify the submitted elements (stated paradigm, core constructs, target population, and setting).
2. **Critique**: Diagnose methodological congruence (e.g., construct granularity, elimination of causal language in qualitative designs, operational definitions in quantitative designs).
3. **Guided Revision Steps**: Deliver 2 to 3 actionable, bite-sized questions or tasks requiring the student to revise their wording. Use bullet points. Do not write a dense paragraph. Make the required user action highly clear. (If the draft is successful, use this section for the Success Directive).

TONE:
Collegial, academically rigorous, direct, and unpadded. Eliminate generic praise ("Great topic!"). Open immediately with the observation and critique."""

# ---------------------------------------------------------
# State Management Initialization
# ---------------------------------------------------------

WELCOME_MESSAGE = """**Welcome to Project SEAN!** ✦ 

I am your interactive methodological coach. This tool is designed for **iterative drafting**:

1. **Select your Methodological Track** in the sidebar.
2. **Use this Chat to Brainstorm:** Don't have a draft yet? Ask me a conceptual question, request an example, or bounce ideas off me down here. 
3. **Draft in the Workspace:** When you have a working draft, paste it into the three numbered boxes above. These boxes hold your working document.
4. **Run Alignment Audit:** Click the button in the sidebar to have me analyze how well your three boxes align. 
5. **Revise & Repeat:** Use my feedback to rewrite your text in the boxes above, then audit again.

*Note: You can export your session notes from the sidebar at any time to share with your advisor or peers.*

*Not sure where to start? Try typing: "Can you show me an example of how this tool works?"*"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
if "problem" not in st.session_state:
    st.session_state.problem = ""
if "purpose" not in st.session_state:
    st.session_state.purpose = ""
if "rq" not in st.session_state:
    st.session_state.rq = ""

def update_drafts():
    st.session_state.problem = st.session_state._problem
    st.session_state.purpose = st.session_state._purpose
    st.session_state.rq = st.session_state._rq

# ---------------------------------------------------------
# Sidebar: Configuration, Tools & Feedback
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### Methodological Track")
    
    methodology_track = st.radio(
        "Select your broad approach:",
        ["Qualitative", "Quantitative", "Mixed Methods"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    run_audit = st.button("🔍 Run Alignment Audit", type="primary", use_container_width=True)
    
    export_text = f"# Project SEAN: Session Summary & Notes\n"
    export_text += f"**Date:** {datetime.datetime.now().strftime('%B %d, %Y - %H:%M')}\n"
    export_text += f"**Methodology:** {methodology_track}\n\n"
    export_text += f"## 1. Problem Statement\n{st.session_state.problem if st.session_state.problem else '[Not drafted]'}\n\n"
    export_text += f"## 2. Purpose Statement\n{st.session_state.purpose if st.session_state.purpose else '[Not drafted]'}\n\n"
    export_text += f"## 3. Research Questions\n{st.session_state.rq if st.session_state.rq else '[Not drafted]'}\n\n"
    export_text += f"---\n## Latest Diagnostic Feedback\n\n"
    
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and "Welcome to Project SEAN" not in msg["content"]:
            export_text += msg["content"]
            break

    st.download_button(
        label="📥 Export Session Notes",
        data=export_text,
        file_name="SEAN_Session_Notes.md",
        mime="text/markdown",
        help="Download your current drafts and the latest AI feedback as a text file for your records.",
        use_container_width=True
    )
    
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
        st.session_state.problem = ""
        st.session_state.purpose = ""
        st.session_state.rq = ""
        st.rerun()

    # Beta Feedback Section
    st.markdown("---")
    st.markdown("### 🛠️ Beta Feedback")
    st.markdown("<span style='font-size: 0.9rem;'>Help improve Project SEAN! Please report bugs or share your UX feedback.</span>", unsafe_allow_html=True)
    
    # NOTE: Change 'your.email@niu.edu' to your actual email address
    st.link_button("✉️ Email Developer", "mailto:your.email@niu.edu?subject=Project%20SEAN%20Beta%20Feedback", use_container_width=True)

# ---------------------------------------------------------
# Main Viewport: Header & Workspace 
# ---------------------------------------------------------
st.markdown('<div class="main-title">✦ Project SEAN</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Systematic Evaluation & Alignment Navigator: A Pedagogical Scaffolding Tool for Graduate Research Proposals</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.text_area("1. Problem Statement", value=st.session_state.problem, height=120, key="_problem", help="What is the specific gap in the literature or practical issue you are addressing? (The Gap)", on_change=update_drafts)
with col2:
    st.text_area("2. Purpose Statement", value=st.session_state.purpose, height=120, key="_purpose", help="What is the overarching goal or intent of your study? (The Intent)", on_change=update_drafts)
with col3:
    st.text_area("3. Research Question(s)", value=st.session_state.rq, height=120, key="_rq", help="What are the specific, answerable questions that will guide your inquiry? (The Inquiry)", on_change=update_drafts)

active_count = sum(1 for text in [st.session_state.problem, st.session_state.purpose, st.session_state.rq] if text.strip())

if active_count == 0:
    st.info("💡 **Status:** Ready for Ideation. Ask a question below or begin drafting.")
    audit_scope = "IDEATION"
elif active_count == 1:
    st.warning("⚠️ **Status:** Isolated Element Audit (1 of 3 Elements Populated)")
    audit_scope = "ISOLATED_ELEMENT"
elif active_count == 2:
    st.warning("⚠️ **Status:** Partial Alignment Audit (2 of 3 Elements Populated)")
    audit_scope = "PARTIAL_ALIGNMENT"
else:
    st.success("✅ **Status:** Ready for Complete Alignment Audit (All 3 Elements Populated)")
    audit_scope = "FULL_ALIGNMENT"

# ---------------------------------------------------------
# Chat Rendering (Scrollable Container) & API Call
# ---------------------------------------------------------
chat_container = st.container(height=380, border=False)

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

chat_input = st.chat_input("Ask a clarifying question, request an example, or test out a concept...")

if run_audit or chat_input:
    ui_display_message = "*(Triggered Alignment Audit)*" if run_audit else chat_input
    system_payload = f"""[USER INPUT]: {ui_display_message}
Current Scope: {audit_scope}
Methodology: {methodology_track}
Problem: {st.session_state.problem}
Purpose: {st.session_state.purpose}
RQ: {st.session_state.rq}"""

    st.session_state.messages.append({"role": "user", "content": ui_display_message})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(ui_display_message)

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=system_payload,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2, 
            ),
        )
        assistant_reply = response.text
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(assistant_reply)
            
    except Exception as e:
        st.error("⚠️ The AI is currently experiencing high demand. Please wait a few seconds and try again.")
        st.session_state.messages.pop()