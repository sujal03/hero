import fitz  # PyMuPDF
import os
import streamlit as st
from PIL import Image
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure you have the NLTK punkt tokenizer downloaded
nltk.download('punkt')

# Function to extract text and images from PDF
def extract_pdf_content(pdf_path):
    pdf_data = {}
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        images = page.get_images(full=True)

        # Store text and images for each page
        pdf_data[f"page_{page_num}"] = {
            "text": text,
            "images": []
        }

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"image_page_{page_num}_{img_index}.png"
            pdf_data[f"page_{page_num}"]["images"].append(image_filename)

            # Save the image
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

    return pdf_data

# Function to handle user queries
def handle_query(query, pdf_data):
    tokens = word_tokenize(query.lower())
    response_text = ""
    response_images = []

    # Search through the extracted PDF data for relevant content
    for page, content in pdf_data.items():
        sentences = sent_tokenize(content["text"])
        matched_sentences = [sent for sent in sentences if all(token in sent.lower() for token in tokens)]
        
        if matched_sentences:
            response_text += " ".join(matched_sentences) + "\n"
            response_images.extend(content["images"])  # Collect images from all relevant content

    return response_text.strip(), response_images

# Path to your PDF file
pdf_path = "glamour-aug-2023.pdf"
pdf_data = extract_pdf_content(pdf_path)

# Streamlit app UI
st.title("PDF Chatbot")

# Input for user query
user_query = st.text_input("Ask something about the PDF")

# Handle query and display results
if st.button("Ask"):
    if user_query:
        response_text, response_images = handle_query(user_query, pdf_data)

        if response_text:
            st.text_area("Response", response_text)
            
            if response_images:
                for img_path in response_images:
                    img = Image.open(img_path)
                    img = img.resize((200, 200), Image.LANCZOS)  # Resize for display
                    st.image(img)
        else:
            st.write("I'm sorry, I couldn't find any relevant information.")
    else:
        st.write("Please enter a query.")
