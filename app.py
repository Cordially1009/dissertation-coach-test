import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Proposal Coach — Pilot", page_icon="🎓")

# 1. API Key Setup
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("Please provide a Gemini API Key to continue.")
    st.stop()

# Sanitize surrounding quotes or whitespace
api_key = api_key.strip().strip('"').strip("'")

# 2. Initialize Google GenAI Client
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing client: {e}")
    st.stop()

# 3. Grounding Prompt (Creswell & Terrell)
SYSTEM_PROMPT = """You are an expert academic research coach auditing doctoral dissertation proposals based on the frameworks of Creswell and Terrell.
Focus Area: Module 2 - Purpose Statements & Research Questions.

Rules:
1. Qualitative inquiry: Reject causal or directional terms (cause, impact, affect, relate, influence). Encourage exploratory language (how, what, explore, describe).
2. Quantitative inquiry: Check for testable variables and comparative or relational structures.
3. Anti-ghostwriting: Never write or rewrite the final question for the student.
4. Always structure your feedback strictly with:
   - **Observation**: What is present in the student's submission.
   - **Critique**: Methodological alignment or issue per Creswell/Terrell.
   - **Socratic Prompt**: One guiding question prompting the student to revise their own wording.
"""

st.title("🎓 Dissertation Proposal Coach")
st.caption("Pilot Test: Purpose Statements & Research Questions")

# 4. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome! Enter a draft research question or purpose statement to audit its methodological alignment.",
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. User Input and Generation
if prompt := st.chat_input("Enter your research question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Auditing question structure..."):
            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                    ),
                )
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as e:
                st.error(f"API Error: {e}")
