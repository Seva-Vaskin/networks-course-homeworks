import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    def __init__(self, sender_email, sender_password, smtp_server, smtp_port):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, recipient_email, subject, message, message_type='plain'):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, message_type))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                print("Email successfully sent!")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Send an email to a specified recipient.")
    parser.add_argument("--recipient")
    parser.add_argument("--subject")
    parser.add_argument("--message")
    parser.add_argument("--type", choices=['plain', 'html'])
    parser.add_argument("--smtp_server")
    parser.add_argument("--smtp_port")
    parser.add_argument("--login")
    parser.add_argument("--password")

    args = parser.parse_args()

    email_sender = EmailSender(args.login, args.password, args.smtp_server, args.smtp_port)
    email_sender.send_email(args.recipient, args.subject, args.message, args.type)


if __name__ == "__main__":
    main()
