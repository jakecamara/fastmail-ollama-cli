import requests
import sys
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
API_URL = os.getenv("API_URL")
OLLAMA_URL = os.getenv("OLLAMA_URL")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Step 1: Get Inbox ID
def get_inbox_id():
    payload = {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": [
            ["Mailbox/get", { "accountId": ACCOUNT_ID }, "0"]
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    mailboxes = response.json()["methodResponses"][0][1]["list"]
    for mailbox in mailboxes:
        if mailbox.get("role") == "inbox":
            return mailbox["id"]
    return None

# Step 2: Fetch Emails in Inbox
def fetch_emails(inbox_id, limit=10):
    payload = {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": [
            [
                "Email/query",
                {
                    "accountId": ACCOUNT_ID,
                    "filter": { "inMailbox": inbox_id },
                    "sort": [{ "property": "receivedAt", "isAscending": False }],
                    "limit": limit
                },
                "0"
            ]
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["methodResponses"][0][1]["ids"]

# Step 3: Fetch Email Details for Selected Email
def get_email_details(email_ids):
    payload = {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": [
            [
                "Email/get",
                {
                    "accountId": ACCOUNT_ID,
                    "ids": email_ids,
                    "properties": ["textBody", "htmlBody", "subject", "from", "blobId"]
                },
                "0"
            ]
        ]
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    email_list = response.json()["methodResponses"][0][1]["list"]

    for email in email_list:
        text_body = email.get("textBody", [])
        html_body = email.get("htmlBody", [])
        blob_id = email.get("blobId")

        # Try to fetch content from blobId in textBody
        if text_body and "blobId" in text_body[0]:
            email["content"] = fetch_full_email_body(text_body[0]["blobId"])
        # Try to fetch content from blobId in htmlBody
        elif html_body and "blobId" in html_body[0]:
            email["content"] = fetch_full_email_body(html_body[0]["blobId"])
        # Fallback to blobId at the email level
        elif blob_id:
            email["content"] = fetch_full_email_body(blob_id)
        else:
            email["content"] = "(No content available)"
    return email_list

# HTML Parser to strip HTML tags
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()

# Fetch content using blobId and strip HTML
def fetch_full_email_body(blob_id):
    # Download the raw content using blobId
    download_url = f"https://www.fastmailusercontent.com/jmap/download/{ACCOUNT_ID}/{blob_id}/"
    response = requests.get(download_url, headers=HEADERS)
    response.raise_for_status()
    html_content = response.text.strip()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove all <style> tags
    for style_tag in soup.find_all("style"):
        style_tag.decompose()  # Remove the tag and its content

    # Get plain text content without HTML tags
    plain_text = soup.get_text()

    # Remove excessive whitespace and return clean content
    return re.sub(r'\s+', ' ', plain_text).strip()

# Step 4: Process with Ollama
def process_with_ollama(prompt):
    payload = {
        "stream": False,
        "model": "llama3",
        "prompt": prompt
    }
    headers = {
        "Content-Type": "application/json"
    }
    # print("\nDEBUG: Sending the following prompt to Ollama:")
    # print(prompt)  # Log the prompt being sent to Ollama
    response = requests.post(OLLAMA_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("response", "No response from Ollama.")

# Interactive CLI
def interactive_email_processor():
    try:
        inbox_id = get_inbox_id()
        if not inbox_id:
            print("Inbox not found.")
            sys.exit(1)

        while True:
            # Fetch and display emails
            email_ids = fetch_emails(inbox_id)
            emails = get_email_details(email_ids)

            print("\nYour Inbox:")
            for i, email in enumerate(emails, start=1):
                sender = email.get("from", [{}])[0].get("name", "Unknown Sender")
                subject = email.get("subject", "(No Subject)")
                print(f"{i}. From: {sender} | Subject: {subject}")

            print("\nOptions:")
            print("Enter the number of the email to process.")
            print("Q: Quit")

            choice = input("Choose an email or action: ").strip().lower()
            if choice == "q":
                print("Goodbye!")
                break

            if choice.isdigit() and 1 <= int(choice) <= len(emails):
                email = emails[int(choice) - 1]
                sender = email.get("from", [{}])[0].get("name", "Unknown Sender")
                subject = email.get("subject", "(No Subject)")
                content = email.get("content", "(No content available)")

                # Debugging: Ensure content is fetched
                # print("\nDEBUG: Content fetched from the email:")
                # print(content)

                # Step 2: Summarize Email
                prompt = (
                    f"Summarize the following email, highlighting key points. Skip all standard marketing email closing content that talks about their social media, address, links to unsubscribe, etc. Also your response should just a summary paragraph, don't include anything introducing the summary. Just the summary in as many sentences as are required to cover all points.\n\n"
                    f"Sender: {sender}\n"
                    f"Subject: {subject}\n"
                    f"Content:\n{content}"
                )
                # print("\nDEBUG: Sending the following prompt to Ollama:")
                # print(prompt)

                print(f"\nOllama is summarizing your email...")
                summary = process_with_ollama(prompt)
                print(f"\nSummary:\n{summary}")

                # Step 3: Next Actions
                while True:
                    print("\nOptions:")
                    print("1: Review another email")
                    print("2: Generate a reply to this email")
                    print("Q: Quit")

                    action = input("Choose an action: ").strip().lower()
                    if action == "1":
                        break
                    elif action == "2":
                        # Generate Reply
                        reply_prompt = f"Write a polite and professional reply to the following email:\n\nSender: {sender}\nSubject: {subject}\nContent: {content}"
                        reply = process_with_ollama(reply_prompt)
                        print(f"\nGenerated Reply:\n{reply}")
                        break
                    elif action == "q":
                        print("Goodbye!")
                        sys.exit(0)
                    else:
                        print("Invalid option. Please try again.")
            else:
                print("Invalid choice. Please try again.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the interactive processor
if __name__ == "__main__":
    interactive_email_processor()