import streamlit as st

# State variables to track uploaded files and enable button
uploaded_questionnaire = None
uploaded_docs = None

def generate_report(questionnaire, docs):
  st.success("Report is being generated...")
  # Process files
  # Simulate processing time
  import time
  time.sleep(2)
  st.success("Report generation complete!")

st.set_page_config(page_title="Hackathon-XFactor: ESG Survey automation Questionnaire & Report App", layout="wide")

# Custom CSS to set sidebar width (consider using a separate CSS file for maintainability)
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 40%;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
  st.header("Upload Files")

  uploaded_questionnaire = st.file_uploader("Upload Questionnaire (XLSX)", type="xlsx")
  uploaded_docs = st.file_uploader("Upload Supporting Documents (PDF)", type="pdf")

  # Enable GenerateReport button only if both files are uploaded
  generate_report_button = st.button("Generate Report", disabled=(not uploaded_questionnaire or not uploaded_docs))

  if generate_report_button:
    generate_report(uploaded_questionnaire.read(), uploaded_docs.read())

# Chat-based app on the main content area
st.header("Q & A Chatbot")

message = st.text_input("Ask a question...")


