from .services import GetBradescoReceipts
from .sentry import capture_exception
from datetime import datetime
from .helpers import (
    Mailer, log, send_slack_message,
    formatting_slack_message
)
from io import BytesIO
from app import celery
import zipfile
import os


@celery.task(bind=True, max_retries=3)
def get_receipt_task(self, renavams_list, state):
    result = dict(
        success_list=[],
        fail_list=[]
    )
    try:
        get_bradesco = GetBradescoReceipts(renavams_list, state)
        result = get_bradesco.result
    except Exception as exception:
        try:
            self.retry(renavams_list=renavams_list, state=state)
        except Exception:
            capture_exception(exception)

    if len(result['success_list']) > 0:
        log('Zip files')
        destination_file = BytesIO()
        zip_file = zipfile.ZipFile(destination_file, mode="w")
        for folder, subfolders, files in os.walk('temp'):
            for file in files:
                zip_file.write(
                    os.path.join(folder, file),
                    os.path.relpath(os.path.join(folder, file), 'temp'),
                    compress_type=zipfile.ZIP_DEFLATED
                )
                os.remove(os.path.join(folder, file))
            zip_file.close()
        os.rmdir('temp')

        log('Write email')
        mail = Mailer(
            email=os.environ.get("BRADESCO_RECEIPTS_EMAIL"),
            content=[]
        )

        log('Add zip as attachment')
        today = datetime.today()
        timestamp = today.strftime("%Y%m%d%H%m%s")
        file_name = f'recibos-bradesco-{state}-{timestamp}.zip'
        mail.append_attachments(
            file=destination_file.getvalue(),
            name=file_name,
            type='application/pdf'
        )

        log('Send...')
        try:
            sent = mail.deliver()
            if sent:
                log("Success!")
            else:
                log("Fail!")
        except Exception as error:
            log(f'Fail! {error}')
    else:
        log('Receips not found!')

    slack_endpoint = os.environ.get('SLACK_BRADESCO_RECEIPTS_ENDPOINT')
    body = formatting_slack_message(result, state)
    result = send_slack_message(slack_endpoint, body)
