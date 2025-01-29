import streamlit as st
import time
import fitz  # PyMuPDF
import easyocr
import speech_recognition as sr  # Voice Input
from groq import Groq
from PIL import Image

class AIStudyAssistant:
    def __init__(self):
        self.client = Groq(api_key="YOUR_GROQ_API_KEY")  # Replace with your actual API key
        self.reader = easyocr.Reader(['en'], gpu=False)  # OCR reader

        if 'text_responses' not in st.session_state:
            st.session_state.text_responses = []
        if 'image_responses' not in st.session_state:
            st.session_state.image_responses = []
        if 'pdf_responses' not in st.session_state:
            st.session_state.pdf_responses = []

    def get_ai_response(self, input_text, topic_type):
        if "exact answer" in input_text.lower():
            return "Sorry, I can't give exact answers. I'm here to help you think critically!"

        system_message = f"""
        You are an AI study assistant. Provide hints but do not give direct answers. 
        Focus strictly on {topic_type}-related hints.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_message},
                          {"role": "user", "content": input_text}],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            st.error(f"Error getting AI response: {str(e)}")
            return None

    def process_voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now!")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                st.warning("Sorry, I couldn't understand the audio.")
                return None
            except sr.RequestError:
                st.warning("Could not request results, check your internet.")
                return None

    def render_ui(self):
        st.set_page_config(page_title="AI Study Assistant", layout="wide")
        st.sidebar.image("img.png", width=250)
        self.topic_type = st.sidebar.radio("Topic type:", ("General", "Coding", "Math", "Science"))

        st.markdown("<h1>AI Study Assistant</h1>", unsafe_allow_html=True)
        text_tab, voice_tab = st.tabs(["Text Input", "Voice Input"])

        with text_tab:
            user_input = st.text_area("Enter your question:")
            if st.button("Get Response"):
                if user_input:
                    hint = self.get_ai_response(user_input, self.topic_type)
                    if hint:
                        st.markdown(f"**AI Response:** {hint}")
                else:
                    st.warning("Please enter a question.")

        with voice_tab:
            if st.button("🎤 Speak Now"):
                with st.spinner("Listening..."):
                    voice_text = self.process_voice_input()
                    if voice_text:
                        st.text_area("Recognized Speech:", voice_text)
                        hint = self.get_ai_response(voice_text, self.topic_type)
                        if hint:
                            st.markdown(f"**AI Response:** {hint}")

if __name__ == "__main__":
    assistant = AIStudyAssistant()
    assistant.render_ui()
