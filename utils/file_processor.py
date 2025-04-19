# utils/file_processor.py

import pdfplumber
import camelot
import pandas as pd
import io
import tempfile
import os
import docx2txt
import pytesseract
from PIL import Image
import cv2
import numpy as np
import streamlit as st

@st.cache_data
def process_uploaded_file(uploaded_file, enable_ocr=False):
    """
    Process uploaded files (PDF, TXT, DOCX) and extract text and tables
    
    Args:
        uploaded_file: The uploaded file object
        enable_ocr: Whether to use OCR for scanned documents
        
    Returns:
        tuple: (extracted_text, tables)
    """
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return process_pdf(uploaded_file, enable_ocr)
    elif file_extension == 'txt':
        text = uploaded_file.read().decode("utf-8")
        return text, []
    elif file_extension == 'docx':
        text = docx2txt.process(uploaded_file)
        return text, []
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def process_pdf(pdf_file, enable_ocr=False):
    """Process PDF files to extract text and tables"""
    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        # Extract text using pdfplumber
        with pdfplumber.open(tmp_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                
                # If page has no text and OCR is enabled, apply OCR
                if not page_text and enable_ocr:
                    # Convert page to image
                    img = page.to_image()
                    # Save image to temporary file
                    img_path = f"{tmp_path}_page.png"
                    img.save(img_path)
                    
                    # Apply OCR
                    image = Image.open(img_path)
                    page_text = pytesseract.image_to_string(image)
                    
                    # Clean up
                    os.remove(img_path)
                
                if page_text:
                    pages_text.append(page_text)
            
            text = "\n".join(pages_text)
        
        # Extract tables using Camelot
        tables = []
        try:
            table_data = camelot.read_pdf(tmp_path, pages='all', flavor='stream')
            if len(table_data) > 0:
                for i in range(len(table_data)):
                    tables.append(table_data[i].df)
        except Exception as e:
            st.warning(f"Table extraction error: {str(e)}")
        
        return text, tables
    
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)

def preprocess_text(text):
    """Clean and normalize text for better analysis"""
    import re
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'[\r\n]+', '\n', text)
    
    # Fix common OCR errors
    text = text.replace('l', 'I').replace('0', 'O')
    
    return text.strip()