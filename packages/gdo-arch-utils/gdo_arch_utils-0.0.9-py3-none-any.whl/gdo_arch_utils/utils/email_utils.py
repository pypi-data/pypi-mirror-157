from gdo_arch_utils.utils.file_utils import FileUtils as file_utils
from email.message import EmailMessage
import smtplib
import traceback
from dataclasses import dataclass
from gdo_arch_utils.utils.log_utils import LogUtils as log_utils

logger = log_utils.get_logger()


@dataclass(frozen = True)
class EmailUtils:
	host: str
	port: int
	username: str
	password: str

	def send_email(
		self,
		subject,
		mail_body,
		receiver_mails,
		sender_mail,
		file_name,
		mail_attachment_text = None
	) -> bool:
		try:
			email_message = EmailMessage()
			email_message['Subject'] = subject
			email_message['From'] = sender_mail
			email_message['To'] = receiver_mails
			email_message.add_alternative(mail_body, subtype = 'html')
			if mail_attachment_text:
				email_message.add_attachment(
					mail_attachment_text, subtype = 'text', filename = file_name
				)
			with smtplib.SMTP(self.host, self.port) as smtp:
				logger.info("Connected to SMTP server")
				smtp.ehlo()
				smtp.starttls()
				smtp.ehlo()
				smtp.login(self.username, self.password)
				smtp.send_message(email_message)
				logger.info("Mail sent")
			return True
		except Exception as ex:
			traceback.print_exc()
			return False

	@classmethod
	def from_json(cls, smtp_vault_path):
		sftp_json_str = file_utils.get_json_from_file(smtp_vault_path)
		return cls(
			port = int(sftp_json_str["Port"]),
			host = sftp_json_str["AmazonServer"],
			username = sftp_json_str["SES_Access_Key_ID"],
			password = sftp_json_str["Access_Key_Password"]
		)
