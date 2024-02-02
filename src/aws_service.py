import boto3
from src.config import settings

from botocore.exceptions import BotoCoreError, ClientError


class SessionSingleton:
    _instance = None

    @classmethod
    def get_instance(cls, aws_access_key_id, aws_secret_access_key):
        if cls._instance is None:
            session = boto3.Session(
                aws_secret_access_key=aws_secret_access_key,
                aws_access_key_id=aws_access_key_id,
            )
            cls._instance = session
        return cls._instance


class SESSingleton:
    _instance = None

    def __new__(
        cls, aws_access_key_id, aws_secret_access_key, region_name, endpoint_url
    ):
        if cls._instance is None:
            session = SessionSingleton.get_instance(
                aws_access_key_id, aws_secret_access_key
            )
            cls._instance = session.client(
                "ses", region_name=region_name, endpoint_url=endpoint_url
            )

        return cls._instance


class SESService:
    def __init__(self):
        self.aws_access_key_id = settings.localstack_access_key_id
        self.aws_secret_access_key = settings.localstack_secret_access_key
        self.region_name = settings.localstack_region_name
        self.endpoint_url = settings.localstack_endpoint_url

    def _ses_session(self):
        return SESSingleton(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.region_name,
            self.endpoint_url,
        )

    def _perform_ses_action(self, action_callback):
        try:
            session = self._ses_session()
            return action_callback(session)
        except BotoCoreError as err:
            raise ConnectionError(f"Error interacting with SES: {err}")

    def send_email(self, subject, body, sender, recipients):
        def send_email_action(ses):
            try:
                response = ses.send_email(
                    Source=sender,
                    Destination={"ToAddresses": recipients},
                    Message={
                        "Subject": {"Data": subject},
                        "Body": {"Text": {"Data": body}},
                    },
                )
                return response
            except ClientError as err:
                raise ConnectionError(f"Error sending email: {err}")

        return self._perform_ses_action(send_email_action)

    def verify_email(self, email):
        def verify_email_action(ses):
            try:
                response = ses.verify_email_identity(EmailAddress=email)
                return response
            except ClientError as err:
                raise ConnectionError(f"Error verifying email: {err}")

        return self._perform_ses_action(verify_email_action)
