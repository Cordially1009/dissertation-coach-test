import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Methodology Coach Test", layout="centered")

# 1. API Key Handling (Checks Cloud Secrets, falls back to manual entry)
api_key = st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("Paste your Gemini API key in the sidebar to begin testing.")
    st.stop()

client = genai.Client(api_key=api_key)

# 2. Minimal Pilot Grounding (Creswell/Terrell Rule Test)
SYSTEM_PROMPT = """
You are an academic research coach auditing dissertation research questions.
Rules:
- If the question is qualitative, reject directional or causal terms (e.g., 'cause', 'impact', 'affect', 'relate'). Advise exploratory phrasing ('how', 'what').
- Do not write the question for the student. Provide 1 observation, 1 critique, and 1 Socratic question.
"""

# 3. Maintain Chat Session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Paste a draft research question, and I'll audit its methodological phrasing."}
    ]

st.title("🎓 Proposal Coach — Pilot Test")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Handle Input & Call Model
if prompt := st.chat_input("Enter your research question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )

    assistant_reply = response.text
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)