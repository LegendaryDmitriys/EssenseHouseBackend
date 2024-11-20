from django.core.mail import send_mail
from django.conf import settings
import imaplib
import email
from email.header import decode_header



def send_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False,
    )


def fetch_emails(category='inbox'):
    imap_server = 'imap.gmail.com'
    email_user = settings.EMAIL_HOST_USER
    email_pass = settings.EMAIL_HOST_PASSWORD


    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_user, email_pass)

    if category == 'sent':
        print("Selecting 'Sent Mail' folder...")
        status, _ = mail.select('"[Gmail]/Sent Mail"')
    elif category == 'spam':
        print("Selecting 'Spam' folder...")
        status, _ = mail.select(('[Gmail]/Spam'))
    else:
        print("Selecting 'Inbox' folder...")
        status, _ = mail.select('inbox')

    if status != 'OK':
        print(f"Failed to select folder: {category}")
        mail.logout()
        return []

    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print("Failed to search emails")
        mail.logout()
        return []

    email_ids = messages[0].split()
    print(f"Fetching emails from category: {category}, Total emails found: {len(email_ids)}")

    fetched_emails = []

    for email_id in email_ids[-10:]:
        print(f"Fetching email ID: {email_id.decode('utf-8')}")
        _, msg_data = mail.fetch(email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')
                from_ = msg.get('From')

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                fetched_emails.append({
                    "subject": subject,
                    "from": from_,
                    "body": body,
                })

    mail.logout()
    return fetched_emails