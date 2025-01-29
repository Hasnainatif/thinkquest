import streamlit as st
import time
import fitz  # PyMuPDF
import easyocr
from PIL import Image
from groq import Groq

class AIStudyAssistant:
    def __init__(self):
        """
        Initialize the AI study assistant:
        - Sets up the Groq client using the API key stored in Streamlit secrets.
        - Initializes session states for text, image, and PDF responses.
        - Initializes the EasyOCR reader (for English).
        """
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.reader = easyocr.Reader(['en'], gpu=False)  # Use GPU=True if available

        # Initialize session states if they don't already exist
        if 'text_responses' not in st.session_state:
            st.session_state.text_responses = []
        if 'image_responses' not in st.session_state:
            st.session_state.image_responses = []
        if 'pdf_responses' not in st.session_state:
            st.session_state.pdf_responses = []

    def get_ai_response(self, input_text, topic_type):
        """
        Sends user input text to the Groq API and returns the AI-generated response.
        Includes a safeguard: if the user demands exact answers, it responds with a refusal.
        """
        if "exact answer" in input_text.lower() or "exact solution" in input_text.lower():
            return (
                "Sorry, I can't give exact answers. I am created to boost creativity "
                "and critical thinking skills among students."
            )

        try:
            system_message = (
                "You are an AI study assistant focusing on educational topics. "
                "Provide hints and approaches to solve problems, but do not give exact answers. "
                "Ensure each hint fosters curiosity and deeper thinking. "
                f"Focus strictly on {topic_type}-related hints. "
                "If a user demands an exact answer, politely refuse."
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
        """
        Use EasyOCR to extract text from the uploaded image.
        Returns the extracted text as a string.
        """
        try:
            image_file.seek(0)
            with open("temp_image.png", "wb") as f:
                f.write(image_file.read())
            results = self.reader.readtext("temp_image.png", detail=0)
            extracted_text = " ".join(results)
            return extracted_text
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_file):
        """
        Extract text from an uploaded PDF using PyMuPDF.
        Returns the combined text from all pages.
        """
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

    def render_ui(self):
        """
        Sets up the main UI layout:
        - Page config
        - Sidebar
        - Tabs for text, image, PDF input
        - Footer and progress bar
        """
        self.setup_page()
        self.render_sidebar()
        self.render_tabs()

    def setup_page(self):
        """
        Configure the page and load custom CSS styling with a more modern, advanced look.
        """
        st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")
        st.markdown(
            """
            <style>
                /* Overall background gradient */
                .stApp {
                    background: linear-gradient(to bottom right, #fafbfc, #f0f4f8);
                    font-family: "Arial", sans-serif;
                }
                
                body {
                    margin: 0;
                    padding: 0;
                    color: #2C3E50;
                }
                
                /* Main container for content */
                .response-card {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #E0E4EB;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
                    transition: 0.3s ease;
                }
                .response-card:hover {
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
                }
                
                .hint-text {
                    background-color: #F7F9FA;
                    color: #2C3E50;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 6px solid #3498DB;
                }
                
                /* Buttons */
                .stButton > button {
                    background-color: #3498DB;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 0.9rem;
                    transition: 0.2s ease;
                }

                .stButton > button:hover {
                    background-color: #2980b9;
                    transform: translateY(-1px);
                }

                /* Sidebar styling */
                .stSidebar {
                    background-color: #D6DCE5;
                    border-right: 1px solid #BDC3C7;
                }
                
                /* Headers */
                .main-header {
                    color: #5D6D7E;
                    font-size: 2.5em;
                    text-align: center;
                    margin-top: 2rem;
                    margin-bottom: 0.25em;
                    font-weight: bold;
                }
                .sub-header {
                    color: #7F8C8D;
                    font-size: 1.3em;
                    text-align: center;
                    margin-bottom: 2rem;
                }
                
                /* Footer */
                .footer {
                    background-color: #ECF0F1;
                    color: #2C3E50;
                    text-align: center;
                    padding: 10px;
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                    left: 0;
                    border-top: 1px solid #BDC3C7;
                }

                /* Tabs */
                .stTabs [data-baseweb="tab-list"] {
                    gap: 10px;
                    background-color: #F2F4F6;
                    border-radius: 8px 8px 0 0;
                    padding: 0 10px;
                }
                .stTabs [data-baseweb="tab"] {
                    height: 50px;
                    border-radius: 6px 6px 0 0;
                    color: #2C3E50;
                    margin: 0 5px;
                    padding: 0 20px;
                }
                .stTabs [aria-selected="true"] {
                    background-color: #3498DB;
                    color: #ffffff;
                    box-shadow: none;
                }
                
                /* Inputs and file uploaders */
                .stTextArea textarea {
                    background-color: #ffffff;
                    color: #2C3E50;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                }
                .stFileUploader {
                    background-color: #ffffff;
                    color: #2C3E50;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 10px;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self):
        """
        Render the sidebar with a logo (optional) and a topic type selector.
        """
        st.sidebar.image("img.png", width=250)
        self.topic_type = st.sidebar.radio("Topic Type:", ("General", "Coding", "Math", "Science"))

    def render_tabs(self):
        """
        Create three tabs: Text Input, Image Input, and PDF Input.
        """
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
        """
        Text input tab: allows the user to input text and receive AI hints.
        """
        user_input = st.text_area("Enter your question below:")
        if st.button("Get Hint (Text)"):
            with st.spinner("Analyzing your question..."):
                if user_input:
                    hint = self.get_ai_response(user_input, self.topic_type)
                    if hint:
                        self.display_ai_hint(hint, "text", user_input)
                else:
                    st.warning("Please enter a question.")
        self.display_previous_responses('text')

    def render_image_tab(self):
        """
        Image input tab: user can upload an image, and the system will extract text
        then provide an AI response. The processed text remains hidden.
        """
        image_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"])
        if st.button("Get Hint (Image)"):
            with st.spinner("Extracting text from your image..."):
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
        """
        PDF input tab: user can upload a PDF, and the system will extract text,
        then provide an AI response. The processed text remains hidden.
        """
        pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if st.button("Get Hint (PDF)"):
            with st.spinner("Analyzing your PDF..."):
                if pdf_file:
                    text = self.extract_text_from_pdf(pdf_file)
                    if text:
                        hint = self.get_ai_response(text, self.topic_type)
                        if hint:
                            self.display_ai_hint(hint, "pdf", text)
                else:
                    st.warning("Please upload a PDF file.")
        self.display_previous_responses('pdf')

    def display_ai_hint(self, hint, source_type, raw_text):
        """
        Displays the AI-generated hint in a response card.
        Also stores the raw_text in session state if needed.
        """
        st.markdown("<div class='response-card'>", unsafe_allow_html=True)
        st.markdown("### AI Hint:")
        st.markdown(f'<div class="hint-text">{hint}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Store responses in session state
        if source_type == 'text':
            st.session_state.text_responses.append((raw_text, hint))
        elif source_type == 'image':
            st.session_state.image_responses.append((raw_text, hint))
        elif source_type == 'pdf':
            st.session_state.pdf_responses.append((raw_text, hint))

    def display_previous_responses(self, response_type):
        """
        Renders previous responses (without showing the extracted text).
        Only shows the AI-generated hints saved in session state.
        """
        if response_type == 'text' and st.session_state.text_responses:
            st.subheader("Previous Text Responses:")
            self.render_responses(st.session_state.text_responses, "Question", "AI Hint")
        elif response_type == 'image' and st.session_state.image_responses:
            st.subheader("Previous Image Responses:")
            self.render_responses(st.session_state.image_responses, "Raw Data (hidden)", "AI Hint")
        elif response_type == 'pdf' and st.session_state.pdf_responses:
            st.subheader("Previous PDF Responses:")
            self.render_responses(st.session_state.pdf_responses, "Raw Data (hidden)", "AI Hint")

    def render_responses(self, responses, input_label, hint_label):
        """
        General method to display stored hints without showing extracted text.
        """
        for i, (input_text, hint) in enumerate(reversed(responses), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>{input_label} {i}:</h4>", unsafe_allow_html=True)
            st.write("(Not shown)")
            st.markdown(f"<h4>{hint_label} {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="hint-text">{hint}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    def render_footer(self):
        """
        Adds a footer at the bottom of the page.
        """
        st.markdown(
            "<div class='footer'>© 2024 ThinkQuest. All rights reserved.</div>",
            unsafe_allow_html=True,
        )

    def render_progress_bar(self):
        """
        Shows a progress bar in the sidebar for a visual loading effect.
        """
        progress_bar = st.sidebar.progress(0)
        for i in range(100):
            time.sleep(0.005)  # Slightly faster progress for a smoother feel
            progress_bar.progress(i + 1)
        st.sidebar.success("Ready!")

if __name__ == "__main__":
    assistant = AIStudyAssistant()
    assistant.render_ui()
