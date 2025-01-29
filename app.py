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
        - Initializes session states for text, image, and PDF outputs.
        - Initializes the EasyOCR reader (for English).
        """
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.reader = easyocr.Reader(['en'], gpu=False)  # Use GPU=True if available

        # Initialize session states if they don't already exist
        if 'text_outputs' not in st.session_state:
            st.session_state.text_outputs = []
        if 'image_outputs' not in st.session_state:
            st.session_state.image_outputs = []
        if 'pdf_outputs' not in st.session_state:
            st.session_state.pdf_outputs = []
        if 'theme' not in st.session_state:
            st.session_state.theme = 'Light'

    def get_ai_output(self, input_text, topic_type):
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
                "Provide insights and approaches to solve problems, but do not give exact answers. "
                f"Focus strictly on {topic_type}-related content. "
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
        - Sidebar with theme toggle and topic type
        - Tabs for text, image, and PDF
        - Footer and progress bar
        """
        self.setup_page()
        self.render_sidebar()
        self.render_tabs()

    def setup_page(self):
        """
        Configures the page based on selected theme.
        """
        st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")

        # Conditional CSS for Light or Dark
        if st.session_state.theme == "Dark":
            css_style = """
            <style>
                .stApp {
                    background: #1E1E1E;
                    color: #F0F0F0;
                }
                .response-card {
                    background-color: #2A2D2E;
                    color: #F0F0F0;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #444;
                    box-shadow: 0 4px 8px rgba(255, 255, 255, 0.05);
                }
                .response-card:hover {
                    box-shadow: 0 8px 16px rgba(255, 255, 255, 0.08);
                }
                .response-text {
                    background-color: #333;
                    border-left: 6px solid #3498DB;
                }
                .stButton > button {
                    background-color: #3498DB !important;
                    color: #ffffff !important;
                    border-radius: 6px;
                }
                .stButton > button:hover {
                    background-color: #2980b9 !important;
                }
                .stSidebar {
                    background-color: #2A2D2E !important;
                }
                .stFileUploader, .stTextArea textarea {
                    background-color: #333 !important;
                    color: #F0F0F0 !important;
                }
                .footer {
                    background-color: #2A2D2E;
                    color: #F0F0F0;
                    border-top: 1px solid #444;
                }
                .main-header {
                    color: #ffffff;
                }
                .sub-header {
                    color: #cccccc;
                }
            </style>
            """
        else:
            css_style = """
            <style>
                .stApp {
                    background: linear-gradient(to bottom right, #fafbfc, #f0f4f8);
                }
                .response-card {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #E0E4EB;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
                }
                .response-card:hover {
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
                }
                .response-text {
                    background-color: #F7F9FA;
                    border-left: 6px solid #3498DB;
                }
                .stButton > button {
                    background-color: #3498DB !important;
                    color: #ffffff !important;
                    border: none;
                    border-radius: 6px;
                }
                .stButton > button:hover {
                    background-color: #2980b9 !important;
                }
                .stSidebar {
                    background-color: #D6DCE5 !important;
                }
                .stFileUploader, .stTextArea textarea {
                    background-color: #ffffff !important;
                    color: #2C3E50 !important;
                    border: 1px solid #dee2e6 !important;
                    border-radius: 6px;
                }
                .footer {
                    background-color: #ECF0F1;
                    color: #2C3E50;
                    border-top: 1px solid #BDC3C7;
                }
                .main-header {
                    color: #5D6D7E;
                }
                .sub-header {
                    color: #7F8C8D;
                }
            </style>
            """

        st.markdown(css_style, unsafe_allow_html=True)

    def render_sidebar(self):
        """
        Renders the sidebar with a logo, a theme toggle, and a topic type selector.
        """
        st.sidebar.image("img.png", width=200)
        # Theme toggle
        st.session_state.theme = st.sidebar.radio("Select Theme:", ("Light", "Dark"))
        # Topic type radio
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
        Text input tab: allows the user to input text and receive an AI response.
        """
        user_input = st.text_area("Ask your question here:")
        if st.button("Generate Response (Text)"):
            with st.spinner("Analyzing your question..."):
                if user_input:
                    output = self.get_ai_output(user_input, self.topic_type)
                    if output:
                        self.display_ai_response(output, "text", user_input)
                else:
                    st.warning("Please enter a question first.")
        self.display_previous_outputs('text')

    def render_image_tab(self):
        """
        Image input tab: user can upload an image, and the system will extract text
        then provide an AI response. The raw text is not displayed.
        """
        image_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"])
        if st.button("Generate Response (Image)"):
            with st.spinner("Extracting text from your image..."):
                if image_file:
                    extracted_text = self.process_image(image_file)
                    if extracted_text:
                        output = self.get_ai_output(extracted_text, self.topic_type)
                        if output:
                            self.display_ai_response(output, "image", extracted_text)
                else:
                    st.warning("Please upload an image file.")
        self.display_previous_outputs('image')

    def render_pdf_tab(self):
        """
        PDF input tab: user can upload a PDF, and the system will extract text,
        then provide an AI response. The raw text is not displayed.
        """
        pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if st.button("Generate Response (PDF)"):
            with st.spinner("Analyzing your PDF..."):
                if pdf_file:
                    text = self.extract_text_from_pdf(pdf_file)
                    if text:
                        output = self.get_ai_output(text, self.topic_type)
                        if output:
                            self.display_ai_response(output, "pdf", text)
                else:
                    st.warning("Please upload a PDF file.")
        self.display_previous_outputs('pdf')

    def display_ai_response(self, response_text, source_type, raw_text):
        """
        Displays the AI-generated response in a container.
        Also stores the raw_text in session state for future reference.
        """
        st.markdown("<div class='response-card'>", unsafe_allow_html=True)
        st.markdown("### AI Response:")
        st.markdown(f'<div class="response-text" style="padding: 15px; margin: 10px 0;">{response_text}</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Save responses in session state
        if source_type == 'text':
            st.session_state.text_outputs.append((raw_text, response_text))
        elif source_type == 'image':
            st.session_state.image_outputs.append((raw_text, response_text))
        elif source_type == 'pdf':
            st.session_state.pdf_outputs.append((raw_text, response_text))

    def display_previous_outputs(self, output_type):
        """
        Renders previous outputs without showing the extracted text.
        Only shows the AI-generated response saved in session state.
        """
        if output_type == 'text' and st.session_state.text_outputs:
            st.subheader("Previous Text Responses:")
            self.render_responses(st.session_state.text_outputs, "Text Query", "Response")
        elif output_type == 'image' and st.session_state.image_outputs:
            st.subheader("Previous Image Responses:")
            self.render_responses(st.session_state.image_outputs, "Extracted Content (hidden)", "Response")
        elif output_type == 'pdf' and st.session_state.pdf_outputs:
            st.subheader("Previous PDF Responses:")
            self.render_responses(st.session_state.pdf_outputs, "Extracted Content (hidden)", "Response")

    def render_responses(self, outputs, input_label, response_label):
        """
        Displays stored responses without showing the processed input text in detail.
        """
        for i, (input_text, response_text) in enumerate(reversed(outputs), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>{input_label} {i}:</h4>", unsafe_allow_html=True)
            st.write("(Not shown)")
            st.markdown(f"<h4>{response_label} {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="response-text" style="padding: 15px; margin: 10px 0;">{response_text}</div>',
                        unsafe_allow_html=True)
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
        Shows a progress bar in the sidebar for visual loading effect.
        """
        progress_bar = st.sidebar.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress_bar.progress(i + 1)
        st.sidebar.success("Ready!")

if __name__ == "__main__":
    assistant = AIStudyAssistant()
    assistant.render_ui()
