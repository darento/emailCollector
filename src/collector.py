import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import PyPDF2
import matplotlib.pyplot as plt


APP_PASSWORD = os.getenv("APP_PASSWORD")


class EmailCollector:
    def __init__(self, username, password):
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.mail.login(username, password)
        self.mail.select("inbox")

    def fetch_emails(self):
        result, data = self.mail.uid("search", None, "ALL")
        email_ids = data[0].split()
        return email_ids

    def download_attachments(self, email_id):
        result, email_data = self.mail.uid("fetch", email_id, "(BODY.PEEK[])")
        raw_email = email_data[0][1].decode("utf-8")
        email_message = email.message_from_string(raw_email)
        for part in email_message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue
            fileName = part.get_filename()

            if bool(fileName):
                filePath = os.path.join("/downmails/", fileName)
                os.makedirs(os.path.dirname(filePath), exist_ok=True)
                if not os.path.isfile(filePath):
                    with open(filePath, "wb") as f:
                        f.write(part.get_payload(decode=True))


def parse_pdfs(file_path):
    pdf_file_obj = open(file_path, "rb")
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    page_obj = pdf_reader.getPage(0)
    text = page_obj.extractText()
    pdf_file_obj.close()
    return text


def generate_charts(data):
    plt.figure(figsize=(10, 5))
    plt.bar(data.keys(), data.values())
    plt.show()


if __name__ == "__main__":
    print("Starting email collector...")
    username = "dsartiom@gmail.com"
    with open("../test.app", "r") as f:
        password = f.read()
    email_collector = EmailCollector(username, password)
    email_ids = email_collector.fetch_emails()
    for email_id in email_ids:
        email_collector.download_attachments(email_id)
    print("Emails downloaded successfully!")
