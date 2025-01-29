import streamlit as st
import os
from groq import Groq
import pytesseract
from PIL import Image
import io
import requests
import time
import fitz  # PyMuPDF

class AIStudyAssistant:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path for Windows
        self.initialize_session_state()

    def initialize_session_state(self):
        if 'text_responses' not in st.session_state:
            st.session_state.text_responses = []
        if 'image_responses' not in st.session_state:
            st.session_state.image_responses = []
        if 'pdf_responses' not in st.session_state:
            st.session_state.pdf_responses = []

    def process_image(self, image_file):
        try:
            image = Image.open(image_file)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_file):
        try:
            text = ""
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None

    def get_ai_response(self, input_text, topic_type):
        try:
            system_message = """you are an AI study assistant. Provide hints and approaches to solve problems, but don't give exact answers. 
            When crafting your response, consider the following prompts and guidelines: the answer should be versatile and arise curiosity in the user and do not reveal the exact answers give them hints to...
            Ensure each hint is unique and encourages critical thinking. Focus on {topic_type}-related """
            if topic_type == "Coding":
                system_message += "Focus on coding-related topics and provide specific coding hints."
            elif topic_type == "Math":
                system_message += "Focus on math-related topics and provide specific mathematical hints."
            elif topic_type == "Science":
                system_message += "Focus on science-related topics and provide specific scientific hints."
            else:
                system_message += "Focus on general education-related topics."

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": input_text,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error getting AI response: {str(e)}")
            return None

    def render_ui(self):
        self.setup_page()
        self.render_sidebar()
        self.render_tabs()

    def setup_page(self):
        st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")
        st.markdown("""
        <style>
            .stApp { background: linear-gradient(to bottom right, #E0E5EC, #C2CCD6); }
            body { color: #2C3E50; font-family: 'Arial', sans-serif; }
            .stContainer { max-width: 800px; margin: 0 auto; }
            .response-card { background-color: #FFFFFF; color: #2C3E50; border-radius: 10px; padding: 20px; margin: 20px 0; border: 1px solid #BDC3C7; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
            .hint-text { background-color: #ECF0F1; color: #2C3E50; border-radius: 10px; padding: 15px; margin-top: 20px; border-left: 5px solid #3498DB; }
            .stButton > button { background-color: #3498DB; color: white; border: none; border-radius: 5px; padding: 10px 20px; }
            .stSidebar { background-color: #D6DCE5; color: #2C3E50; }
            .main-header { background: linear-gradient(45deg, #3498DB, #2980B9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3em; text-align: center; animation: fadeInDown 1s ease-out; }
            .sub-header { background: linear-gradient(45deg, #E74C3C, #C0392B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.5em; text-align: center; animation: fadeInUp 1s ease-out; }
            .footer { background: linear-gradient(45deg, #BDC3C7, #95A5A6); color: #2C3E50; text-align: center; padding: 10px; position: fixed; bottom: 0; width: 100%; left: 0; animation: fadeIn 1s ease-out; }
            @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            .stTabs [data-baseweb="tab-list"] { gap: 20px; padding: 0 10px; }
            .stTabs [data-baseweb="tab"] { height: 50px; background-color: #D6DCE5; color: #2C3E50; border-radius: 5px 5px 0 0; margin: 0 5px; padding: 0 20px; }
            .stTabs [aria-selected="true"] { background-color: #3498DB; color: white; }
            .response-card h4 { color: #2C3E50; }
            .stTextArea textarea { background-color: #FFFFFF; color: #2C3E50; border: 1px solid #BDC3C7; }
            .stFileUploader { background-color: #FFFFFF; color: #2C3E50; border: 1px solid #BDC3C7; border-radius: 5px; padding: 10px; }
        </style>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        st.sidebar.image("img.png", width=250)
        self.topic_type = st.sidebar.radio("Topic type:", ("General", "Coding", "Math", "Science"))

    def render_tabs(self):
        st.markdown("<h1 class='main-header'>AI Study Assistant</h1>", unsafe_allow_html=True)
        st.markdown("<h2 class='sub-header'>Welcome! How can I assist you today?</h2>", unsafe_allow_html=True)
        text_tab, image_tab, pdf_tab = st.tabs(["Text Input", "Image Input", "PDF Input"])
        
        with text_tab:
            self.render_text_tab()

        with image_tab:
            self.render_image_tab()

        with pdf_tab:
            self.render_pdf_tab()

        self.render_footer()
        self.render_progress_bar()

    def render_text_tab(self):
        user_input = st.text_area("Enter your question:")
        if st.button("Get Hint (Text)"):
            with st.spinner("Processing..."):
                if user_input:
                    hint = self.get_ai_response(user_input, self.topic_type)
                    if hint:
                        self.display_response(user_input, hint, 'text')
                else:
                    st.warning("Please enter a question.")
        self.display_previous_responses('text')

    def render_image_tab(self):
        image_file = st.file_uploader("Upload image file", type=["png", "jpg", "jpeg"])
        if st.button("Get Hint (Image)"):
            with st.spinner("Processing..."):
                if image_file:
                    text = self.process_image(image_file)
                    if text:
                        hint = self.get_ai_response(text, self.topic_type)
                        if hint:
                            self.display_response(text, hint, 'image')
                else:
                    st.warning("Please upload an image.")
        self.display_previous_responses('image')

    def render_pdf_tab(self):
        pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
        if st.button("Get Hint (PDF)"):
            with st.spinner("Processing..."):
                if pdf_file:
                    text = self.extract_text_from_pdf(pdf_file)
                    if text:
                        hint = self.get_ai_response(text, self.topic_type)
                        if hint:
                            self.display_response(text, hint, 'pdf')
                else:
                    st.warning("Please upload a PDF file.")
        self.display_previous_responses('pdf')

    def display_response(self, question, hint, response_type):
        st.markdown("<div class='response-card'>", unsafe_allow_html=True)
        st.markdown("### Processed text:" if response_type != 'text' else "### Hint:")
        st.write(question[:500] + "..." if len(question) > 500 else question)
        st.markdown("### Hint:")
        st.markdown(f'<div class="hint-text">{hint}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if response_type == 'text':
            st.session_state.text_responses.append((question, hint))
        elif response_type == 'image':
            st.session_state.image_responses.append((question, hint))
        elif response_type == 'pdf':
            st.session_state.pdf_responses.append((question, hint))

    def display_previous_responses(self, response_type):
        if response_type == 'text' and st.session_state.text_responses:
            st.markdown("### Previous Text Responses:")
            self.render_responses(st.session_state.text_responses)
        elif response_type == 'image' and st.session_state.image_responses:
            st.markdown("### Previous Image Responses:")
            self.render_responses(st.session_state.image_responses)
        elif response_type == 'pdf' and st.session_state.pdf_responses:
            st.markdown("### Previous PDF Responses:")
            self.render_responses(st.session_state.pdf_responses)

    def render_responses(self, responses):
        for i, (question, answer) in enumerate(reversed(responses), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>Processed Text {i}:</h4>", unsafe_allow_html=True)
            st.write(question[:500] + "..." if len(question) > 500 else question)
            st.markdown(f"<h4>Answer {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="hint-text">{answer}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if i < len(responses):
                st.markdown("<div class='response-divider'></div>", unsafe_allow_html=True)

    def render_footer(self):
        st.markdown("<div class='footer'>© 2024 ThinkQuest. All rights reserved.</div>", unsafe_allow_html=True)

    def render_progress_bar(self):
        progress_bar = st.sidebar.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        st.sidebar.success("Ready!")

if __name__ == "__main__":
    assistant = AIStudyAssistant()
    assistant.render_ui()
