###############################
## Collects the IP Fabric part number inventory
## Then creates a csv file
## Then emails via SMTP
##
## Relies on v6.9 of IP Fabric - adjust URL if using a different version
###############################


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os

# API authentication
IPFABRIC_API_URL = 'https://<server>/api/v6.9/tables/inventory/pn'
API_TOKEN = '<your_token_here>'

# Supress only InsecureRequestWarning - if using self signed cert
def disable_specific_warning():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Function to fetch part numbers from IP Fabric API
def fetch_part_numbers():
    headers = {
        "Content-Type": "application/json",
        "X-API-Token": API_TOKEN,
    }

    # Payload for the API request
    payload = {
        "columns": ["hostname",
            "deviceSn",
            "siteName",
            "deviceId",
            "name",
            "dscr",
            "pid",
            "sn",
            "vid",
            "vendor",
            "platform",
            "model"
            ],
        "snapshot": "$last",
        "filters": {},              # Add filters if needed

    }

    response = requests.post(IPFABRIC_API_URL, headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

# Save part numbers to a CSV file
def save_to_csv(part_numbers, filename):
    df = pd.DataFrame(part_numbers, columns=["hostname",
            "deviceSn",
            "siteName",
            "deviceId",
            "name",
            "dscr",
            "pid",
            "sn",
            "vid",
            "vendor",
            "platform",
            "model"  ])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Function to send email with CSV attachment
def send_email_with_attachment(recipient_email, subject, body, attachment_path, sender_email, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the body of the email
    msg.attach(MIMEText(body, 'plain'))

    # Attach the CSV file
    attachment = open(attachment_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {attachment_path}")
    msg.attach(part)

    # Log in to server and send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

    print(f"Email sent to {recipient_email}")

# Main script logic
if __name__ == "__main__":
    # Remove warnings because of using no cert validation
    disable_specific_warning()

    # Fetch the part numbers
    part_numbers = fetch_part_numbers()

    # Save part numbers to CSV
    if part_numbers:
        csv_filename = "part_numbers.csv"
        save_to_csv(part_numbers, csv_filename)

        # Email credentials and recipient info
        recipient_email = "destination@example.com"  # Replace with actual recipient
        sender_email = "source@email.com"  # Replace with actual sender's email
        sender_password = "smtp_password"  # Replace with actual sender's email password

        # Email content
        subject = "IP Fabric Part Numbers"
        body = "Please find the attached CSV file containing the IP Fabric part numbers."

        # Send email with CSV attachment
        send_email_with_attachment(recipient_email, subject, body, csv_filename, sender_email, sender_password)
    else:
        print("No part numbers found.")
