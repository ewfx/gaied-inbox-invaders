import streamlit as st
import csv
import tempfile
import os
from collections import defaultdict
from readMsg import readmsg
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the CSV file with request types and build the dictionary
csv_filename = "requestTypes.csv"
requests_dict = defaultdict(list)
with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:
            key, value = row
            requests_dict[key].append(value)
requests_dict = dict(requests_dict)

# Initialize the Google GenAI client
google_api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=google_api_key)

st.title("Email Structured Information Extraction")
st.write("Upload one or more email (.msg) files from your system:")

# File uploader to select multiple email files
uploaded_files = st.file_uploader("Select Email Files", type=["msg"], accept_multiple_files=True)

if st.button("Process Emails"):
    if not uploaded_files:
        st.error("Please upload at least one email file.")
    else:
        results = {}
        for uploaded_file in uploaded_files:
            try:
                # Write uploaded file to a temporary file so readmsg can process it
                with tempfile.NamedTemporaryFile(delete=False, suffix=".msg") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                # Extract email content using readmsg
                email_content = readmsg(tmp_path)
                
                # Remove temporary file after processing
                os.remove(tmp_path)
                
                # Build the prompt with the CSV requests and the email content
                prompt = f"""
You are an assistant that extracts structured information from an email.
Input 1 (Requests): {requests_dict}
Input 2 (Email): {email_content}

Extract the following into JSON format:
- "Request Type": The main request category that best matches the email content (choose one from the keys of Input 1).
- "Sub Request type": The correct sub request based on the Request Type from Input 1.
- "Other details": All other important details extracted from the email that are not the request type or sub request type.

Return the result strictly as a valid JSON object.
"""
                # Send the prompt to the model
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                results[uploaded_file.name] = response.text
            except Exception as e:
                results[uploaded_file.name] = f"Error processing email: {str(e)}"
        st.write("Extraction Results:")
        st.json(results)
