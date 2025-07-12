
import streamlit as st
import openai
import json
import os

# --- 1. Configuration & API Key Loading ---
# Load the OpenAI API key from Replit Secrets (environment variables)
# The key name OPENAI_API_KEY is what we set in Replit Secrets
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    st.error("Error: OPENAI_API_KEY not found in Replit Secrets. Please add it.")
    st.stop() # Stop the Streamlit app if API key is missing

# Configure the OpenAI library with your API key
openai.api_key = OPENAI_API_KEY

# --- 2. Load iAssist's Knowledge Base from JSON File ---
# Make sure your JSON file is uploaded to the root of your Replit project
FAQ_FILE = "manual_faqs.json" # <--- IMPORTANT: Ensure this matches your uploaded file name!

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
# This assumes your JSON is a list of objects like: [{"question": "...", "answer": "..."}, ...]
faq_context = ""
for item in faqs_data:
    if "question" in item and "answer" in item:
        faq_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"
    # You can add more logic here if your JSON has different structures or fields
    # Example: if 'topic' in item: faq_context += f"Topic: {item['topic']}\n"

# --- 3. iAssist System Prompt Template ---
# This is adapted from your previous prompt, designed for OpenAI's chat completions.
system_prompt_template = """
You are iAssist, an expert BMW product specialist and virtual Genius. Your core function is to provide clear, concise, and accurate information about BMW features and services. You are equipped with a specialized knowledge base on iDrive 8, Parking Assistant Professional, BMW ConnectedDrive services, electric vehicle charging for BMW iX, Head-up Display, and frequently asked questions from BMW service advisors.

---
**Relevant Context from BMW Knowledge Base:**
{context}
---

When a user asks a question, first determine if the question relates to your pre-defined topics or provided context. If relevant information is supplied, use that information to formulate your answer. If a question is outside your knowledge scope or no relevant information is found, politely state that you can only provide information on the features you are familiar with. Prioritize providing solutions to common issues and clear explanations of features. Keep your answers factual and directly answer the user's query.
"""

# --- 4. Streamlit Application Interface ---
st.set_page_config(page_title="BMW FAQ AI Assistant", page_icon="🚗")

# --- Add a sidebar for information or controls ---
with st.sidebar:
    st.header("About This Assistant")
    st.write("This AI Assistant is designed to answer your questions about BMW vehicles, drawing information from a specialized set of FAQs. It's powered by OpenAI's ChatGPT-4o model.")
    st.write("Feel free to ask questions about BMW features, services, or common troubleshooting tips found in the FAQs.")
    st.markdown("---")
    st.write("Created by Avery Phillips")

    # --- Add a "Clear Chat" Button ---
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun() # Rerun the app to clear the display

# Optional: Add a logo at the top of the main page
# Make sure you upload 'bmw_logo.png' to your Replit project if you use this
try:
    st.image("bmw_logo.png", width=100) # <--- THIS LINE IS NOW UNCOMMENTED
except FileNotFoundError:
    st.warning("BMW logo image not found. Please upload 'bmw_logo.png' to the root directory of your Replit project.")


st.title("BMW FAQ AI Assistant 🚗")
st.markdown("Ask me anything about BMW vehicles from our official FAQs!")

# Add custom styling for white background and complementary colors
st.markdown(
    """
    <style>
    /* Override Streamlit's default dark theme */
    .stApp {
        background-color: white !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, .css-1cypcdb, section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg .stMarkdown, .css-1lcbmhc .stMarkdown, section[data-testid="stSidebar"] .stMarkdown {
        color: #2c3e50 !important;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    /* User message styling */
    [data-testid="chat-message-user"] {
        background-color: #e8f4fd !important;
        color: #1e3a8a !important;
    }
    
    /* Assistant message styling */
    [data-testid="chat-message-assistant"] {
        background-color: #f1f5f9 !important;
        color: #334155 !important;
    }
    
    /* Headers styling */
    h1, h2, h3 {
        color: #1e40af !important;
    }
    
    /* All text elements */
    .stMarkdown, .stText, p, div {
        color: #2c3e50 !important;
    }
    
    /* Instruction text styling */
    .instruction-text {
        color: #4f46e5 !important;
        font-size: 1.05em;
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1e40af !important;
        color: white !important;
        border: none !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input, .stChatInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    /* Chat input container */
    .stChatInput {
        background-color: white !important;
    }
    
    /* Override any remaining dark elements */
    .css-1v0mbdj, .css-12oz5g7, .css-184tjsw {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    </style>
    <p class="instruction-text">Type your question below about BMW features, services, or common issues, and I'll do my best to provide an answer from my knowledge base.</p>
    """,
    unsafe_allow_html=True
)


# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input via chat_input
if prompt := st.chat_input("Ask a question about BMW..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare the messages for the OpenAI API call
                # Include the system prompt first, then the full chat history for context
                messages_for_api = [
                    {"role": "system", "content": system_prompt_template.format(context=faq_context)}
                ] + st.session_state.messages # Append previous chat turns for context

                response = openai.chat.completions.create(
                    model="gpt-4o",  # Recommended for latest model access. Or "gpt-4", "gpt-3.5-turbo" if preferred.
                    messages=messages_for_api, # Use the full message history
                    max_tokens=500,  # Limit response length
                    temperature=0.2  # Lower temperature for more factual/less creative responses
                )
                ai_response = response.choices[0].message.content
                st.markdown(ai_response) # Use st.markdown for AI's response

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

            except openai.APIError as e:
                st.error(f"An OpenAI API error occurred: {e}. Please check your API key, model access, or network.")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"}) # Add error to history
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"}) # Add error to history

# --- Optional: Display Raw FAQs for debugging/reference ---
# with st.expander("View Loaded FAQs"):
#     st.json(faqs_data)
