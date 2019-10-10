import asyncio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scripts.config import BOT_MAIL, BOT_MAIL_PASSWORD, MAIL_RECEPIENT
import aiosmtplib


async def send_photo(bytes_photos, name, phone):
    message = MIMEMultipart("alternative")
    message["From"] = BOT_MAIL
    message["To"] = MAIL_RECEPIENT
    message["Subject"] = "Telegram Bot: Photo search"

    html_message = MIMEText(
        '''<html>
<body>Help find by photo</body>

<h1>{0}</h1>
<h1>{1}</h1>
</html>'''.format(name, phone), "html", "utf-8"
    )

    message.attach(html_message)
    for bytes_photo in bytes_photos:
        message.attach(MIMEImage(bytes_photo.getvalue()))
    await aiosmtplib.send(message, hostname="mail.service-market.com.ua", port=25, recipients=[MAIL_RECEPIENT],
    username=BOT_MAIL,
    password=BOT_MAIL_PASSWORD)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_photo())
