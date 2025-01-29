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
        self.reader = easyocr.Reader(['en'], gpu=False)  # Use GPU=True if you have GPU support

        # Initialize session state
        if 'text_responses' not in st.session_state:
            st.session_state.text_responses = []
        if 'image_responses' not in st.session_state:
            st.session_state.image_responses = []
        if 'pdf_responses' not in st.session_state:
            st.session_state.pdf_responses = []

    def process_image(self, image_file):
        """
        Use EasyOCR to extract text from an uploaded image.
        The 'image_file' is a file-like object uploaded in Streamlit.
        """
        try:
            image_file.seek(0)  # Reset file pointer
            with open("temp_image.png", "wb") as f:
                f.write(image_file.read())
            
            # Use EasyOCR to read the saved image file
            results = self.reader.readtext("temp_image.png", detail=0)
            # Join results into one string
            extracted_text = " ".join(results)
            return extracted_text
        except Exception as e:
            st.error(f"Error processing image with EasyOCR: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_file):
        """
        Extract text from an uploaded PDF using PyMuPDF.
        The 'pdf_file' is a file-like object uploaded in Streamlit.
        """
        try:
            text = ""
            pdf_file.seek(0)  # Reset file pointer
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None

    def get_ai_response(self, input_text, topic_type):
        """
        Send the user input text to the Groq API and get back an AI-generated hint or response.
        The 'topic_type' parameter modifies the system message to focus on a specific subject.
        """
        try:
            # Construct a system message tailored to the topic type
            system_message = (
                "You are an AI study assistant. Provide hints and approaches to solve problems, "
                "but don't give exact answers. When crafting your response, consider the following "
                "prompts and guidelines: the answer should be versatile and elicit curiosity. "
                "Ensure each hint is unique and encourages critical thinking. "
                f"Focus on {topic_type}-related "
            )

            # Extend system message with details
            if topic_type == "Coding":
                system_message += "topics and provide specific coding hints."
            elif topic_type == "Math":
                system_message += "topics and provide specific mathematical hints."
            elif topic_type == "Science":
                system_message += "topics and provide specific scientific hints."
            else:
                system_message += "general education topics."

            # Send to Groq for completion
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": input_text},
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content

        except Exception as e:
            st.error(f"Error getting AI response from Groq: {str(e)}")
            return None

    def render_ui(self):
        """
        Main function that builds the UI with Streamlit:
        - Page setup
        - Sidebar for topic selection
        - Tabs for text, image, and PDF input
        - Previous responses display
        """
        self.setup_page()
        self.render_sidebar()
        self.render_tabs()

    def setup_page(self):
        """
        Configure Streamlit page and apply custom CSS styles.
        """
        st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")
        st.markdown(
            """
            <style>
                .stApp {
                    background: linear-gradient(to bottom right, #E0E5EC, #C2CCD6);
                }
                body {
                    color: #2C3E50;
                    font-family: 'Arial', sans-serif;
                }
                .stContainer {
                    max-width: 800px;
                    margin: 0 auto;
                }
                .response-card {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #BDC3C7;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .hint-text {
                    background-color: #ECF0F1;
                    color: #2C3E50;
                    border-radius: 10px;
                    padding: 15px;
                    margin-top: 20px;
                    border-left: 5px solid #3498DB;
                }
                .stButton > button {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                }
                .stSidebar {
                    background-color: #D6DCE5;
                    color: #2C3E50;
                }
                .main-header {
                    background: linear-gradient(45deg, #3498DB, #2980B9);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 3em;
                    text-align: center;
                    animation: fadeInDown 1s ease-out;
                }
                .sub-header {
                    background: linear-gradient(45deg, #E74C3C, #C0392B);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 1.5em;
                    text-align: center;
                    animation: fadeInUp 1s ease-out;
                }
                .footer {
                    background: linear-gradient(45deg, #BDC3C7, #95A5A6);
                    color: #2C3E50;
                    text-align: center;
                    padding: 10px;
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                    left: 0;
                    animation: fadeIn 1s ease-out;
                }
                @keyframes fadeInDown {
                    from {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                    }
                    to {
                        opacity: 1;
                    }
                }
                .stTabs [data-baseweb="tab-list"] {
                    gap: 20px;
                    padding: 0 10px;
                }
                .stTabs [data-baseweb="tab"] {
                    height: 50px;
                    background-color: #D6DCE5;
                    color: #2C3E50;
                    border-radius: 5px 5px 0 0;
                    margin: 0 5px;
                    padding: 0 20px;
                }
                .stTabs [aria-selected="true"] {
                    background-color: #3498DB;
                    color: white;
                }
                .response-card h4 {
                    color: #2C3E50;
                }
                .stTextArea textarea {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #BDC3C7;
                }
                .stFileUploader {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #BDC3C7;
                    border-radius: 5px;
                    padding: 10px;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self):
        """
        Render the sidebar with a logo and a topic type radio selector.
        """
        st.sidebar.image("img.png", width=250)
        self.topic_type = st.sidebar.radio("Topic type:", ("General", "Coding", "Math", "Science"))

    def render_tabs(self):
        """
        Create tabs for text input, image input, and PDF input.
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
        Render the text input tab, including a text area and a button to get a hint.
        """
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
        """
        Render the image input tab, including an uploader and a button to process the image.
        """
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
        """
        Render the PDF input tab, including an uploader and a button to process the PDF.
        """
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
        """
        Display the AI hint or processed text based on the input type.
        """
        st.markdown("<div class='response-card'>", unsafe_allow_html=True)
        
        if response_type != 'text':
            st.markdown("### Processed text:")
            preview = question if len(question) < 500 else question[:500] + "..."
            st.write(preview)
            st.markdown("### Hint:")
        else:
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
        """
        Display previous responses, grouped by text, image, or PDF.
        """
        if response_type == 'text' and st.session_state.text_responses:
            st.markdown("### Previous Text Responses:")
            self.render_responses(st.session_state.text_responses, "Question", "Answer")
        elif response_type == 'image' and st.session_state.image_responses:
            st.markdown("### Previous Image Responses:")
            self.render_responses(st.session_state.image_responses, "Processed Text", "Answer")
        elif response_type == 'pdf' and st.session_state.pdf_responses:
            st.markdown("### Previous PDF Responses:")
            self.render_responses(st.session_state.pdf_responses, "Processed Text", "Answer")

    def render_responses(self, responses, question_label, answer_label):
        """
        Helper method to display a list of (question, answer) pairs with a designated format.
        """
        for i, (question, answer) in enumerate(reversed(responses), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>{question_label} {i}:</h4>", unsafe_allow_html=True)
            preview = question if len(question) < 500 else question[:500] + "..."
            st.write(preview)
            st.markdown(f"<h4>{answer_label} {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="hint-text">{answer}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if i < len(responses):
                st.markdown("<div class='response-divider'></div>", unsafe_allow_html=True)

    def render_footer(self):
        """
        Renders a fixed footer at the bottom of the page.
        """
        st.markdown(
            "<div class='footer'>© 2024 ThinkQuest. All rights reserved.</div>",
            unsafe_allow_html=True,
        )

    def render_progress_bar(self):
        """
        Shows a progress bar in the sidebar for visual feedback.
        """
        progress_bar = st.sidebar.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        st.sidebar.success("Ready!")


if __name__ == "__main__":
    assistant = AIStudyAssistant()
    assistant.render_ui()
