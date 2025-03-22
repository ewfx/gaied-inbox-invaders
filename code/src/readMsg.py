import os
from pypdf import PdfReader
from docx import Document
import extract_msg
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        text = f"Error reading PDF file {pdf_path}: {e}"
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        text = f"Error reading DOCX file {docx_path}: {e}"
    return text

def readmsg(path):
    # Load the .msg file
    msg = extract_msg.Message(path)

    # Access email details
    subject = msg.subject
    body = msg.body

    # Initialize final text with subject and body
    final_text = f"Subject: {subject}\n\nBody:\n{body}\n"

    # Save and process attachments
    attachments_dir = 'attachments'
    os.makedirs(attachments_dir, exist_ok=True)
    msg.saveAttachments(attachments_dir)
    
    for attachment in msg.attachments:
        #attachment_path = os.path.join(attachments_dir, attachment.longFilename)
        attachment_path = attachment.longFilename
        if attachment.longFilename.lower().endswith('.pdf'):
            attachment_text = extract_text_from_pdf(attachment_path)
            final_text += f"\n\nAttachment ({attachment.longFilename}):\n{attachment_text}\n"
        elif attachment.longFilename.lower().endswith('.docx'):
            attachment_text = extract_text_from_docx(attachment_path)
            final_text += f"\n\nAttachment ({attachment.longFilename}):\n{attachment_text}\n"
        else:
            final_text += f"\n\nAttachment ({attachment.longFilename}): Unsupported file type.\n"
        os.remove(attachment_path)
    return final_text

#print(readmsg("Emails/KYC_AML Verification - Loan #654321.msg"))
