import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def save_backup_html(html_content):
    with open("report_backup.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    logging.info("Saved report_backup.html to disk.")

def send_email(subject, html_content, to_email, gmail_user, gmail_pass):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Daily News Hunter <{gmail_user}>"
    msg['To'] = to_email
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        logging.info("Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=20)
        server.starttls()
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)
        server.quit()
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        save_backup_html(html_content)
