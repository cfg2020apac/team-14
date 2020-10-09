import os
import requests
MAILGUNKEY = os.getenv('MAILGUNKEY')


def sendMessage(to, subject, text):
    return requests.post(
        "https://api.mailgun.net/v3/delaundro.me/messages",
        auth=("api", MAILGUNKEY),
        data={"from": "Admin <admin@delaundro.me>",
              "to": to,
              "subject": subject,
              "text":  text,
              "o:tracking": False})
