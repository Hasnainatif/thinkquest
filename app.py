import streamlit as st
import time
import fitz  # PyMuPDF
import easyocr
import speech_recognition as sr
from PIL import Image
from groq import Groq

class AIStudyAssistant:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.reader = easyocr.Reader(['en'], gpu=False)  # Use GPU=True if available
        if 'text_responses' not in st.session_state:
            st.session_state.text_responses = []
        if 'image_responses' not in st.session_state:
            st.session_state.image_responses = []
        if 'pdf_responses' not in st.session_state:
            st.session_state.pdf_responses = []

    def get_ai_response(self, input_text, topic_type):
        if "exact answer" in input_text.lower() or "exact solution" in input_text.lower():
            return ("Sorry, I can't give exact answers. I am created to boost creativity and critical thinking skills among students.")
        
        try:
            system_message = (
                "You are an AI study assistant focusing on educational topics. "
                "Provide hints and approaches to solve problems, but do not give exact answers. "
                "Ensure each hint fosters curiosity and deeper thinking. "
                f"Focus strictly on {topic_type}-related hints. "
                "If a user demands an exact answer, politely refuse and explain you cannot provide it. "
                "Encourage them to discuss the question with you so you can help them by providing hints."
            )
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": input_text},
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error getting AI response: {str(e)}")
            return None

    def process_image(self, image_file):
        try:
            image_file.seek(0)
            with open("temp_image.png", "wb") as f:
                f.write(image_file.read())
            results = self.reader.readtext("temp_image.png", detail=0)
            return " ".join(results)
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_file):
        try:
            text = ""
            pdf_file.seek(0)
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now!")
            try:
                audio = recognizer.listen(source, timeout=5)
                return recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                st.error("Sorry, could not understand the audio.")
                return ""
            except sr.RequestError:
                st.error("Could not request results, please check your internet connection.")
                return ""

    def render_ui(self):
        self.setup_page()
        self.render_sidebar()
        self.render_tabs()

    def setup_page(self):
        st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")
        st.markdown(
            """
            <style>
                .mic-button {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 15px;
                    margin-left: 10px;
                    cursor: pointer;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self):
        st.sidebar.image("img.png", width=250)
        self.topic_type = st.sidebar.radio("Topic type:", ("General", "Coding", "Math", "Science"))

    def render_tabs(self):
        st.markdown("<h1 class='main-header'>AI Study Assistant</h1>", unsafe_allow_html=True)
        text_tab, image_tab, pdf_tab = st.tabs(["Text Input", "Image Input", "PDF Input"])
        
        with text_tab:
            self.render_text_tab()
        with image_tab:
            self.render_image_tab()
        with pdf_tab:
            self.render_pdf_tab()

    def render_text_tab(self):
        user_input = st.text_area("Enter your question:", key="text_input")
        col1, col2 = st.columns([8, 1])
        with col1:
            if st.button("Get Response"):
                with st.spinner("Processing..."):
                    if user_input:
                        hint = self.get_ai_response(user_input, self.topic_type)
                        if hint:
                            self.display_ai_hint(hint, "text", user_input)
                    else:
                        st.warning("Please enter a question.")
        with col2:
            if st.button("🎤", key="mic_button"):
                spoken_text = self.recognize_speech()
                if spoken_text:
                    st.session_state.text_input = spoken_text
                    st.experimental_rerun()
        self.display_previous_responses('text')

    def render_image_tab(self):
        image_file = st.file_uploader("Upload image file", type=["png", "jpg", "jpeg"])
        if st.button("Get Response (Image)"):
            with st.spinner("Processing..."):
                if image_file:
                    extracted_text = self.process_image(image_file)
                    if extracted_text:
                        hint = self.get_ai_response(extracted_text, self.topic_type)
                        if hint:
                            self.display_ai_hint(hint, "image", extracted_text)
                else:
                    st.warning("Please upload an image.")
        self.display_previous_responses('image')

    def render_pdf_tab(self):
        pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
        if st.button("Get Response (PDF)"):
            with st.spinner("Processing..."):
                if pdf_file:
                    text = self.extract_text_from_pdf(pdf_file)
                    if text:
                        hint = self.get_ai_response(text, self.topic_type)
                        if hint:
                            self.display_ai_hint(hint, "pdf", text)
                else:
                    st.warning("Please upload a PDF file.")
        self.display_previous_responses('pdf')

if __name__ == "__main__":
    assistant = AIStudyAssistant()
    assistant.render_ui()
