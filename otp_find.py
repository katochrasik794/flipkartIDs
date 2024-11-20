import imaplib
import email
from email.header import decode_header
import re

# IMAP credentials
IMAP_SERVER = 'idsbanao.com'
IMAP_PORT = 993
EMAIL_PASSWORD = 'Admin@000'


# Function to decode the email content with fallback encodings
def decode_content(content):
    # Try UTF-8 encoding first
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        # If UTF-8 fails, try ISO-8859-1 (Latin-1) or fallback to default encoding
        try:
            return content.decode('iso-8859-1')
        except UnicodeDecodeError:
            return content.decode('ascii', 'ignore')  # Final fallback with ignoring errors


# Function to get the latest OTP from the email inbox
def get_latest_otp(email_id):
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(email_id, EMAIL_PASSWORD)

    # Select the inbox folder
    mail.select("inbox")

    # Search for all emails
    result, data = mail.search(None, 'ALL')

    if result != "OK":
        print("No emails found!")
        return None

    # Get the list of email IDs and fetch the latest email
    email_ids = data[0].split()
    latest_email_id = email_ids[-1]

    # Fetch the email by ID
    result, message_data = mail.fetch(latest_email_id, '(RFC822)')

    if result != "OK":
        print("Failed to fetch the email!")
        return None

    # Parse the email content
    raw_email = message_data[0][1]
    msg = email.message_from_bytes(raw_email)

    # Decode the email subject
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else 'utf-8')
    body = ""

    # If the email message is multipart, iterate over the parts
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Get the body of the email
            if "attachment" not in content_disposition:
                if content_type == "text/plain" or content_type == "text/html":
                    # Try to decode the email body safely using our custom decode function
                    body = decode_content(part.get_payload(decode=True))
                    break
    else:
        # If the email is not multipart, extract the body
        body = decode_content(msg.get_payload(decode=True))

    # Use regex to find the OTP (assuming it's a 6-digit number)
    otp_match = re.search(r'\b\d{6}\b', body)
    otp = otp_match.group(0) if otp_match else None

    mail.logout()

    return otp
