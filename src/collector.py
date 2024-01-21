import imaplib
import email

import os


class EmailCollector:
    def __init__(self, username: str, password: str, imap_url: str) -> None:
        self.username = username
        self.password = password
        self.imap_url = imap_url
        self.mail = None

    def connect(self) -> None:
        """Connect to the email server."""
        self.mail = imaplib.IMAP4_SSL(self.imap_url)
        self.mail.login(self.username, self.password)

    def fetch_emails(self, sender: str) -> list:
        """Search for emails based on the given criteria."""
        self.mail.select("inbox")
        result, data = self.mail.uid("search", None, f"(FROM {sender})")
        email_ids = data[0].split()
        return email_ids

    def download_attachments(self, email_id: str, download_folder: str) -> str:
        """Download PDF attachments from the specified emails."""
        result, email_data = self.mail.uid("fetch", email_id, "(BODY.PEEK[])")
        raw_email = email_data[0][1].decode("utf-8")
        email_message = email.message_from_string(raw_email)
        for part in email_message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue
            file_name = part.get_filename()
            if bool(file_name):
                file_path = os.path.join(download_folder, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                if not os.path.isfile(file_path):
                    with open(file_path, "wb") as f:
                        print(f"Downloading {file_name}...")
                        f.write(part.get_payload(decode=True))
                    print(f"Download of {file_name} completed.")
                else:
                    print(f"File {file_name} already exists!")
        return file_path


if __name__ == "__main__":
    pass
