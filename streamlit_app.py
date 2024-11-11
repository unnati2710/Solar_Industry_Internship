import streamlit as st
import requests
from transformers import pipeline
import re
from io import BytesIO
import fitz  # PyMuPDF for PDF files

import fitz  # PyMuPDF
import io
from warnings import PendingDeprecationWarning

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

        # Format the results to display titles, snippets, and links
        output = ""
        for item in results[:5]:  # Limit to top 5 results for brevity
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            output += f"**{title}**\n{snippet}\n[Link]({link})\n\n"
        return output
    else:
        return "Failed to fetch results. Please try again later."

# Enhanced Wikipedia search function with both summary and link
def wikipedia_search(keyword):
    # Handle cases with no input or invalid search terms
    if not keyword:
        return "Please enter a valid search keyword."

    # URL for Wikipedia's REST API
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for HTTP codes like 404, 500, etc.
        
        # Check if the page is found or not
        data = response.json()
        if 'title' in data and 'extract' in data:
            title = data['title']
            summary = data['extract']
            page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"  # Format the URL
            image_url = data.get('thumbnail', {}).get('source', None)  # Get image URL if available

            # Return the formatted result including summary, title, and page link
            result = f"### {title}\n\n**Summary**:\n{summary}\n\n[Read more on Wikipedia]({page_url})"
            if image_url:
                result += f"\n\n![Image]({image_url})"
            return result
        else:
            return "No information found for this keyword."
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"  # For example, 404 not found
    except Exception as err:
        return f"Error occurred: {err}"  # For other errors (network, JSON, etc.)



def analyze_cv(cv_text):
    keywords = re.findall(r'\b\w+\b', cv_text)
    advice_prompt = f"Career insights for a professional skilled in {', '.join(keywords[:5])}: "
    advice = career_advice_generator(advice_prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]
    return advice

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
        
        # Search Input
        query = st.text_input("Enter your search query:")
        if st.button("Search"):
            if query:
                result = google_search(query)
                # Display result inside an expander for better organization
                with st.expander("Search Results"):
                    st.write(result)
            else:
                st.warning("Please enter a query to search.")

    elif choice == "Career Insights":
        st.subheader("Career Insights")
        st.markdown("""
        *Career Insights* provides tailored advice for your professional growth based on the contents of your CV. Upload your CV and get advice on how to progress in your career.
        """)
        
        uploaded_file = st.file_uploader("Upload your CV (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                cv_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                cv_text = extract_text_from_pdf(uploaded_file)
            else:
                cv_text = None
            
            if cv_text:
                advice = analyze_cv(cv_text)
                st.write(advice)

    elif choice == "Chatopedia":
        st.header("📚 Chatopedia (Wikipedia Search)")
        st.write("Enter a keyword to retrieve information from Wikipedia.")
        
        # Wikipedia Search
        keyword = st.text_input("Enter a keyword for Wikipedia search:")
        if st.button("Search Wikipedia"):
            if keyword:
                summary = wikipedia_search(keyword)
                # Display Wikipedia summary in an organized manner
                with st.expander("Wikipedia Summary"):
                    st.write(summary)
            else:
                st.warning("Please enter a keyword to search.")
                

    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>Developed with ❤️ using Streamlit</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

