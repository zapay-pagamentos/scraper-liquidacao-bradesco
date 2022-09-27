from sendgrid.helpers.mail import (
    Email, Content,
    Substitution, Mail,
    Attachment
)
from datetime import datetime
import urllib.request as urllib
import requests
import sendgrid
import base64
import os


class Mailer():
    API_KEY = os.environ.get('SENDGRID_BRADESCO_RECEIPTS')
    sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
    FROM_EMAIL = os.environ.get('ZAPAY_EMAIL')
    today = datetime.today().strftime('%Y-%m-%d')
    subject = f'Liquidação Bradesco - {today}'

    def __init__(self, **kwargs):
        email = kwargs['email']
        to_email = Email(email)
        from_email = Email("Zapay Pagamentos <{}>".format(self.FROM_EMAIL))
        content = Content('text/html', '.')
        self.content = kwargs['content']
        self.mail = Mail(from_email, self.subject, to_email, content)

    def fill_message_content(self):
        for (key, value) in self.content:
            key = "<%{}%>".format(key)
            self.mail.personalizations[0].add_substitution(
                Substitution(key, value)
            )

    def deliver(self):
        try:
            self.sg.client.mail.send.post(request_body=self.mail.get())
            sent = True
        except urllib.HTTPError:
            sent = False
        return sent

    def append_attachments(self, file, name, type='application/pdf'):
        base64_file = None
        base64_file = base64.b64encode(file).decode()
        attachment = Attachment()
        attachment.type = 'application/pdf'
        attachment.disposition = 'attachment'
        attachment.filename = name
        attachment.content = base64_file
        self.mail.add_attachment(attachment)


def send_slack_message(url, data):
    headers = {"Content-Type": "application/json"}
    return requests.request("POST", url, json=data, headers=headers)


def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[LOG] [{now}] {message}")


def formatting_slack_message(result, state):
    today = datetime.now()
    formatted_today = today.strftime("%d/%m/%Y")
    blocks = list()
    title = {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "Liquidação Bradesco" + " [" + state + "] " + formatted_today
        }
    }
    blocks.append(title)

    success_section = dict(
        type="section"
    )

    success_list = "*Renavams com Sucesso*\n"
    for success in result['success_list']:
        success_list += f"{success}\n"

    success_section['fields'] = [
        dict(
            text=success_list,
            type="mrkdwn"
        )
    ]

    blocks.append(success_section)

    fail_section = dict(
        type="section"
    )

    fail_list = "*Renavams com Falha*\n"
    for fail in result['fail_list']:
        fail_list += f"{fail}\n"

    fail_section['fields'] = [
        dict(
            text=fail_list,
            type="mrkdwn"
        )
    ]

    blocks.append(fail_section)

    return dict(blocks=blocks)
