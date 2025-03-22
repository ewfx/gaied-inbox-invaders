import csv
from collections import defaultdict
from readMsg import readmsg
from google import genai
from dotenv import load_dotenv
import os
load_dotenv()

# Input CSV file name
csv_filename = "requestTypes.csv"

# Dictionary to store the data
requests = defaultdict(list)

# Read the CSV file and transform data
with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) == 2:  # Ensure row has exactly 2 columns
            key, value = row
            requests[key].append(value)

requests = dict(requests)

emailPath = "Emails/KYC_AML Verification - Loan #654321.msg"
email = readmsg(emailPath)

google_api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=google_api_key)

prompt = f"""
You are an assistant that extracts structured information from an email.
Input 1 (Requests): {requests}
Input 2 (Email): {email}

Extract the following into JSON format:
- "Request Type": The main request category that best matches the email content (choose one from the keys of Input 1).
- "Sub Request type": The Correct Sub Request based on the Request Type from Input 1.
- "Other details": All other important details extracted from the email that are not the request type or sub request type.

Return the result strictly as a valid JSON object.
"""
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
)

print(response.text)