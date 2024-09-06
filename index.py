import fitz  # PyMuPDF
import os
import streamlit as st
from PIL import Image
import re
import io

# Function to extract text and images from PDF
def extract_pdf_content(pdf_file):
    pdf_data = {}
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Open PDF from uploaded file

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
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
            image_ext = base_image["ext"]  # Get image extension

            # Store image as bytes instead of saving to a file
            image_filename = f"image_page_{page_num}_{img_index}.{image_ext}"
            pdf_data[f"page_{page_num}"]["images"].append((image_filename, image_bytes))

    return pdf_data

# Function to handle user queries with simplified tokenization
def handle_query(query, pdf_data):
    tokens = re.findall(r'\w+', query.lower())  # Tokenize the query using regex
    response_text = ""
    response_images = []

    # Search through the extracted PDF data for relevant content
    for page, content in pdf_data.items():
        sentences = re.split(r'(?<=[.!?]) +', content["text"])  # Simple sentence tokenization
        matched_sentences = [sent for sent in sentences if all(token in sent.lower() for token in tokens)]

        if matched_sentences:
            response_text += " ".join(matched_sentences) + "\n"
            response_images.extend(content["images"])  # Collect images from all relevant content

    return response_text.strip(), response_images

# Streamlit app UI
st.title("PDF Chatbot")

# Upload PDF
pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

if pdf_file:
    pdf_data = extract_pdf_content(pdf_file)

    # Input for user query
    user_query = st.text_input("Ask something about the PDF")

    # Handle query and display results
    if st.button("Ask"):
        if user_query:
            response_text, response_images = handle_query(user_query, pdf_data)

            if response_text:
                st.text_area("Response", response_text)

                if response_images:
                    for img_filename, img_bytes in response_images:
                        img = Image.open(io.BytesIO(img_bytes))  # Load image from bytes
                        img = img.resize((200, 200), Image.LANCZOS)  # Resize for display
                        st.image(img, caption=img_filename)
            else:
                st.write("I'm sorry, I couldn't find any relevant information.")
        else:
            st.write("Please enter a query.")
