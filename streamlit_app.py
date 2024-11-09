import streamlit as st
import requests
from transformers import pipeline
import re

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

# Function to fetch Wikipedia summary
def wikipedia_search(keyword):
    response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}")
    if response.status_code == 200:
        return response.json().get("extract", "No information found.")
    return "No information found."

# Function to analyze CV and give job insights
def analyze_cv(cv_text):
    # Extract keywords based on simple regex (you could enhance this with NLP)
    keywords = re.findall(r'\b\w+\b', cv_text)
    advice_prompt = f"Career insights for a professional skilled in {', '.join(keywords[:5])}: "
    advice = career_advice_generator(advice_prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]
    return advice

# Streamlit UI Layout
def main():
    st.sidebar.title("Chatbot Navigation")
    choice = st.sidebar.radio("Choose a feature", ["Search Engine", "Career Insights", "Chatopedia"])

    if choice == "Search Engine":
        st.title("Search Engine")
        query = st.text_input("Enter your search query:")
        if st.button("Search"):
            if query:
                result = google_search(query)
                st.write("Search Result:")
                st.write(result)
            else:
                st.warning("Please enter a query to search.")

    elif choice == "Career Insights":
        st.title("Career Insights")
        uploaded_file = st.file_uploader("Upload your CV (text file only)", type="txt")
        if uploaded_file:
            cv_text = uploaded_file.read().decode("utf-8")
            st.write("Extracted CV Content:")
            st.write(cv_text)
            if st.button("Get Career Insights"):
                career_advice = analyze_cv(cv_text)
                st.write("Career Advice:")
                st.write(career_advice)

    elif choice == "Chatopedia":
        st.title("Chatopedia (Wikipedia Search)")
        keyword = st.text_input("Enter a keyword for Wikipedia search:")
        if st.button("Search Wikipedia"):
            if keyword:
                summary = wikipedia_search(keyword)
                st.write("Wikipedia Summary:")
                st.write(summary)
            else:
                st.warning("Please enter a keyword to search.")

if __name__ == "__main__":
    main()
