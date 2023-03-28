from googlesearch import search
import requests
from bs4 import BeautifulSoup
from readability import Document#
import openai

def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

def scrape_main_content(url):
    response = requests.get(url)

    # Try using Readability
    doc = Document(response.text)
    content = doc.summary()
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text('\n', strip=True)

    # Check if Readability provided a satisfactory result (e.g., a minimum length)
    # min_length = 50
    # if len(text) < min_length:
    #     # Fallback to the custom function
    #     text = scrape_main_content_custom(response.text)

    return text

def split_text(text, max_length=8192):
    paragraphs = text.split("\n")
    current_length = 0
    current_chunk = []

    for paragraph in paragraphs:
        if current_length + len(paragraph) + 1 <= max_length:
            current_chunk.append(paragraph)
            current_length += len(paragraph) + 1
        else:
            yield "\n".join(current_chunk)
            current_chunk = [paragraph]
            current_length = len(paragraph) + 1

    if current_chunk:
        yield "\n".join(current_chunk)

def summarize_text(text):
    if text == "":
        return "Error: No text to summarize"
    
    print("Text length: " + str(len(text)) + " characters")
    summaries = []
    chunks = list(split_text(text))

    for i, chunk in enumerate(chunks):
        print("Summarizing chunk " + str(i) + " / " + str(len(chunks)))
        messages = [{"role": "user", "content": "Please summarize the following text, focusing on extracting concise knowledge: " + chunk},]

        response= openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
        )

        summary = response.choices[0].message.content
        summaries.append(summary)
    print("Summarized " + str(len(chunks)) + " chunks.")

    combined_summary = "\n".join(summaries)

    # Summarize the combined summary
    messages = [{"role": "user", "content": "Please summarize the following text, focusing on extracting concise knowledge: " + combined_summary},]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=300,
    )

    final_summary = response.choices[0].message.content
    return final_summary