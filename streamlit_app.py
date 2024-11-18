import streamlit as st
import requests
from transformers import pipeline
import re
import io
from io import BytesIO
import fitz  # PyMuPDF for PDF handling
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize Text Generator for Career Insights
career_advice_generator = pipeline("text-generation", model="distilgpt2")

# API credentials (Replace with your actual credentials)
GOOGLE_API_KEY = 'AIzaSyCUaU3QWKSUUoreDL2u4gxDQ_TCdtmrVKw'
SEARCH_ENGINE_ID = '015221a71c1474441'

# Function to perform a real-time Google search using the Google Custom Search API
def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = data.get("items", [])
        if not results:
            return "No results found."

        output = ""
        for item in results[:5]:  # Limit to top 5 results for brevity
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            output += f"{title}\n{snippet}\n[Link]({link})\n\n"
        return output
    else:
        return "Failed to fetch results. Please try again later."

# Enhanced Wikipedia search function with both summary and link
def wikipedia_search(keyword):
    if not keyword:
        return "Please enter a valid search keyword."
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'title' in data and 'extract' in data:
            title = data['title']
            summary = data['extract']
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            image_url = data.get('thumbnail', {}).get('source', None)
            result = f"### {title}\n\n*Summary*:\n{summary}\n\n[Read more on Wikipedia]({page_url})"
            if image_url:
                result += f"\n\n![Image]({image_url})"
            return result
        else:
            return "No information found for this keyword."
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Error occurred: {err}"

# Extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Analyze CV content for career insights
def analyze_cv(cv_text):
    # Extract keywords using TF-IDF for relevance
    vectorizer = TfidfVectorizer(max_features=10, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([cv_text])
    keywords = vectorizer.get_feature_names_out()

    # Generate multiple career advice suggestions
    advice_list = []
    for skill in keywords:
        advice_prompt = f"Provide career advice for a professional skilled in {skill}:"
        advice = career_advice_generator(advice_prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]
        advice_list.append(f"{skill.capitalize()}: {advice}")
    return "\n\n".join(advice_list)

# Streamlit UI Layout
def main():
    # Sidebar Navigation
    st.sidebar.title("Chatbot Navigation")
    st.sidebar.markdown("---")
    choice = st.sidebar.radio("Choose a feature", ["Search Engine", "Career Insights", "Chatopedia"])

    # Main Header
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Intelligent Chatbot Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>An all-in-one tool for web searches, career insights, and knowledge retrieval.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if choice == "Search Engine":
        st.header("🔍 Search Engine")
        st.write("Enter a search query to retrieve real-time information.")
        query = st.text_input("Enter your search query:")
        if st.button("Search"):
            if query:
                result = google_search(query)
                with st.expander("Search Results"):
                    st.write(result)
            else:
                st.warning("Please enter a query to search.")

    elif choice == "Career Insights":
        st.subheader("Career Insights")
        st.markdown("""
        Career Insights provides tailored advice for your professional growth based on the contents of your CV. Upload your CV and get advice on how to progress in your career.
        """)
        uploaded_file = st.file_uploader("Upload your CV (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                cv_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                cv_text = extract_text_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file format.")
                cv_text = None

            if cv_text:
                advice = analyze_cv(cv_text)
                st.write("### Career Insights")
                st.write(advice)

    elif choice == "Chatopedia":
        st.header("📚 Chatopedia (Wikipedia Search)")
        st.write("Enter a keyword to retrieve information from Wikipedia.")
        keyword = st.text_input("Enter a keyword for Wikipedia search:")
        if st.button("Search Wikipedia"):
            if keyword:
                summary = wikipedia_search(keyword)
                with st.expander("Wikipedia Summary"):
                    st.write(summary)
            else:
                st.warning("Please enter a keyword to search.")

    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>Developed with ❤ using Streamlit</p>", unsafe_allow_html=True)

if _name_ == "_main_":
    main()
