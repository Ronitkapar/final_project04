import PyPDF2
import re

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    
    Args:
        file_path (str or file-like object): Path to the PDF file or a file-like object.
        
    Returns:
        str: Extracted text from the PDF.
    """
    text = ""
    try:
        # Handle both file path string and file-like objects (from Streamlit)
        if isinstance(file_path, str):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        else:
            reader = PyPDF2.PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
        
    return text

def clean_text(text):
    """
    Cleans the extracted text by removing excessive whitespace and newlines.
    
    Args:
        text (str): Raw text.
        
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""
    
    # Replace multiple newlines with a single space
    text = re.sub(r'\n+', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
