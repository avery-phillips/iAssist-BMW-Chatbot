import streamlit as st
import openai
import json
import os

# --- 1. Configuration & API Key Loading ---
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    st.error("Error: OPENAI_API_KEY not found in Replit Secrets. Please add it.")
    st.stop()

openai.api_key = OPENAI_API_KEY

# --- 2. Load iAssist's Knowledge Base from JSON File ---
FAQ_FILE = "manual_faqs.json"

try:
    with open(FAQ_FILE, 'r', encoding='utf-8') as f:
        faqs_data = json.load(f)
except FileNotFoundError:
    st.error(f"Error: '{FAQ_FILE}' not found. Please upload your FAQ JSON file to Replit.")
    st.stop()
except json.JSONDecodeError:
    st.error(f"Error: Could not decode JSON from '{FAQ_FILE}'. Please check its format (e.g., syntax errors).")
    st.stop()

# Format FAQs into a single string to include in the system prompt context
faq_context = ""
for item in faqs_data:
    if "question" in item and "answer" in item:
        faq_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"

# --- 3. iAssist System Prompt Template ---
system_prompt_template = """
You are iAssist, an expert BMW product specialist and virtual Genius. Your core function is to provide clear, concise, and accurate information about BMW features and services. You are equipped with a specialized knowledge base on iDrive 8, Parking Assistant Professional, BMW ConnectedDrive services, electric vehicle charging for BMW iX, Head-up Display, and frequently asked questions from BMW service advisors.

---
**Relevant Context from BMW Knowledge Base:**
{context}
---

When a user asks a question, first determine if the question relates to your pre-defined topics or provided context. If relevant information is supplied, use that information to formulate your answer. If a question is outside your knowledge scope or no relevant information is found, politely state that you can only provide information on the features you are familiar with. Prioritize providing solutions to common issues and clear explanations of features. Keep your answers factual and directly answer the user's query.
"""

# --- 4. Streamlit Application Interface ---
st.set_page_config(
    page_title="iAssist - BMW Expert Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Branded Design ---
st.markdown(
    """
<style>
/* Global App Styling */
.stApp {
background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container */
.main .block-container {
padding-top: 2rem;
padding-bottom: 2rem;
max-width: 1200px;
}

/* Hero Section Styling */
.hero-section {
text-align: center;
padding: 3rem 2rem;
background: white;
border-radius: 20px;
box-shadow: 0 10px 30px rgba(0,0,0,0.1);
margin-bottom: 2rem;
border: 1px solid #e1e8ed;
}

.hero-title {
font-size: 3.5rem;
font-weight: 700;
color: #1a202c;
margin-bottom: 0.5rem;
line-height: 1.2;
}

.hero-subtitle {
font-size: 2.8rem;
font-weight: 600;
color: #3182ce;
margin-bottom: 1.5rem;
}

.hero-description {
font-size: 1.3rem;
color: #4a5568;
max-width: 600px;
margin: 0 auto 2rem auto;
line-height: 1.6;
}

/* Action Buttons */
.action-buttons {
display: flex;
gap: 1rem;
justify-content: center;
flex-wrap: wrap;
margin-bottom: 2rem;
}

.primary-btn {
background: linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%);
color: white;
padding: 15px 35px;
border: none;
border-radius: 25px;
font-size: 1.1rem;
font-weight: 600;
cursor: pointer;
text-decoration: none;
display: inline-block;
transition: all 0.3s ease;
box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4);
}

.primary-btn:hover {
transform: translateY(-2px);
box-shadow: 0 6px 20px rgba(49, 130, 206, 0.6);
}

.secondary-btn {
background: transparent;
color: #3182ce;
padding: 15px 35px;
border: 2px solid #3182ce;
border-radius: 25px;
font-size: 1.1rem;
font-weight: 600;
cursor: pointer;
text-decoration: none;
display: inline-block;
transition: all 0.3s ease;
}

.secondary-btn:hover {
background: #3182ce;
color: white;
transform: translateY(-2px);
}

/* Chat Container */
.chat-container {
background: white;
border-radius: 20px;
padding: 2rem;
box-shadow: 0 10px 30px rgba(0,0,0,0.1);
border: 1px solid #e1e8ed;
margin: 2rem auto;
max-width: 800px;
}

.chat-header {
text-align: center;
margin-bottom: 2rem;
padding-bottom: 1rem;
border-bottom: 2px solid #f7fafc;
}

.chat-title {
font-size: 1.8rem;
font-weight: 600;
color: #2d3748;
margin-bottom: 0.5rem;
}

.chat-subtitle {
color: #718096;
font-size: 1.1rem;
}

/* Chat Messages */
.stChatMessage {
margin: 1rem 0;
border-radius: 15px;
padding: 1rem;
max-width: 85%;
}

/* User messages */
[data-testid="chat-message-user"] {
background: linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%);
color: white;
margin-left: auto;
margin-right: 0;
border-radius: 20px 20px 5px 20px;
box-shadow: 0 3px 10px rgba(49, 130, 206, 0.3);
}

[data-testid="chat-message-user"] .stMarkdown {
color: white;
}

/* Ensure user messages remain white text */
[data-testid="chat-message-user"],
[data-testid="chat-message-user"] *,
.stChatMessage[data-testid="chat-message-user"],
.stChatMessage[data-testid="chat-message-user"] * {
color: white !important;
}

/* Assistant messages - Multiple selector approach to ensure coverage */
[data-testid="chat-message-assistant"],
.stChatMessage[data-testid="chat-message-assistant"],
div[data-testid="chat-message-assistant"] {
background: #f7fafc;
color: #000000 !important;
margin-left: 0;
margin-right: auto;
border: 1px solid #e2e8f0;
border-radius: 20px 20px 20px 5px;
box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

/* Target all text elements within assistant messages */
[data-testid="chat-message-assistant"] *,
.stChatMessage[data-testid="chat-message-assistant"] *,
div[data-testid="chat-message-assistant"] * {
color: #000000 !important;
}

/* Specific targeting for Streamlit's markdown content */
[data-testid="chat-message-assistant"] .stMarkdown,
[data-testid="chat-message-assistant"] .stMarkdown *,
.stChatMessage[data-testid="chat-message-assistant"] .stMarkdown,
.stChatMessage[data-testid="chat-message-assistant"] .stMarkdown * {
color: #000000 !important;
}

/* Target common text elements specifically */
[data-testid="chat-message-assistant"] p,
[data-testid="chat-message-assistant"] span,
[data-testid="chat-message-assistant"] div,
[data-testid="chat-message-assistant"] li,
[data-testid="chat-message-assistant"] h1,
[data-testid="chat-message-assistant"] h2,
[data-testid="chat-message-assistant"] h3,
[data-testid="chat-message-assistant"] h4,
[data-testid="chat-message-assistant"] h5,
[data-testid="chat-message-assistant"] h6 {
color: #000000 !important;
}

/* Alternative approach using CSS class selectors */
.stChatMessage:not([data-testid="chat-message-user"]) {
background: #f7fafc;
color: #000000 !important;
border: 1px solid #e2e8f0;
border-radius: 20px 20px 20px 5px;
box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

.stChatMessage:not([data-testid="chat-message-user"]) * {
color: #000000 !important;
}

/* Fallback - aggressive approach to ensure all chat messages have proper colors */
.stChatMessage {
color: #000000 !important;
}

.stChatMessage * {
color: #000000 !important;
}

/* Override any inherited colors from parent elements */
.stChatMessage .stMarkdown,
.stChatMessage .stMarkdown * {
color: #000000 !important;
}

/* Chat Input - Aggressive fix for black bar issue */
.stChatInput {
background: transparent !important;
border: none !important;
box-shadow: none !important;
}

.stChatInput > div {
background: transparent !important;
}

.stChatInput > div > div {
background: transparent !important;
}

.stChatInput textarea {
background: white !important;
color: #2d3748 !important;
border-radius: 25px !important;
border: 2px solid #e2e8f0 !important;
box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
padding: 15px 20px !important;
font-size: 1rem !important;
}

.stChatInput input {
background: white !important;
color: #2d3748 !important;
border-radius: 25px !important;
border: 2px solid #e2e8f0 !important;
box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
padding: 15px 20px !important;
font-size: 1rem !important;
}

/* Remove ALL black backgrounds from chat input area */
[data-testid="stChatInput"] {
background: transparent !important;
}

[data-testid="stChatInput"] * {
background: transparent !important;
}

[data-testid="stChatInput"] form {
background: transparent !important;
}

[data-testid="stChatInput"] form > div {
background: transparent !important;
}

[data-testid="stChatInput"] form > div > div {
background: transparent !important;
}

/* Target the actual input field only */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
background: white !important;
color: #2d3748 !important;
border-radius: 25px !important;
border: 2px solid #e2e8f0 !important;
box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
padding: 15px 20px !important;
font-size: 1rem !important;
}

/* Fix the bottom sticky area */
.stApp > div:last-child {
background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
}

.stApp > div:last-child > div {
background: transparent !important;
}

.stApp > div:last-child > div > div {
background: transparent !important;
}

.stApp > div:last-child > div > div > div {
background: transparent !important;
}

/* Nuclear option - remove all black backgrounds */
.stApp [data-testid="stChatInput"] {
background: transparent !important;
}

.stApp [data-testid="stChatInput"] > * {
background: transparent !important;
}

.stApp [data-testid="stChatInput"] > * > * {
background: transparent !important;
}

.stApp [data-testid="stChatInput"] > * > * > * {
background: transparent !important;
}

/* Ensure only the input field has white background */
.stApp [data-testid="stChatInput"] textarea,
.stApp [data-testid="stChatInput"] input {
background: white !important;
border-radius: 25px !important;
border: 2px solid #e2e8f0 !important;
box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
}

/* Sidebar Styling */
.css-1d391kg, section[data-testid="stSidebar"] {
background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
color: white;
}

.css-1d391kg .stMarkdown, section[data-testid="stSidebar"] .stMarkdown {
color: white;
}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
color: white;
}

/* Logo styling */
.logo-container {
text-align: center;
margin-bottom: 2rem;
}

/* Responsive design */
@media (max-width: 768px) {
.hero-title {
font-size: 2.5rem;
}

.hero-subtitle {
font-size: 2rem;
}

.action-buttons {
flex-direction: column;
align-items: center;
}

.primary-btn, .secondary-btn {
width: 250px;
}

.chat-container {
margin: 1rem;
padding: 1rem;
}
}
</style>
""",
    unsafe_allow_html=True
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🔧 About iAssist")
    st.write("Your BMW Expert Assistant powered by advanced AI and trained on official BMW documentation.")

    st.markdown("### ✨ Features")
    st.write("• Instant BMW technical support")
    st.write("• 24/7 availability")
    st.write("• Expert-level knowledge base")
    st.write("• Quick troubleshooting")

    st.markdown("---")
    st.write("**Created by Avery Phillips**")

    if st.button("🔄 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Content ---
# Simple Header with Logo
try:
    st.markdown(
        """
<div style="display: flex; justify-content: center; margin-bottom: 1rem;">
<img src="data:image/png;base64,{}" width="120">
</div>
""".format(
            __import__('base64').b64encode(open("bmw_logo.png", "rb").read()).decode()
        ),
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning("BMW logo not found. Please upload 'bmw_logo.png' for complete branding.")

st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #1C69D4; margin-bottom: 0.5rem;">
            iAssist: Your BMW Expert
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about BMW features, maintenance, or troubleshooting..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                messages_for_api = [
                    {"role": "system", "content": system_prompt_template.format(context=faq_context)}
                ] + st.session_state.messages

                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=messages_for_api,
                    max_tokens=500,
                    temperature=0.2
                )

                ai_response = response.choices[0].message.content
                st.markdown(ai_response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

            except openai.APIError as e:
                st.error(f"An OpenAI API error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})

# Footer
st.markdown(
    """
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: #718096;">
<p>💡 <strong>Tip:</strong> For best results, be specific about your BMW model and year when asking questions.</p>
<hr style="margin: 2rem 0; border: none; height: 1px; background: #e2e8f0;">
<p><em>iAssist - Independent Demo for Evaluation • Not an Official BMW Product</em></p>
</div>
""",
    unsafe_allow_html=True
)