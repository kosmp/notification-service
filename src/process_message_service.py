import json

from src.logging_config import logger
from src.schemas import PasswordResetMessageSchemaBase
from src.config import settings
from src.aws_service import SESService
from src.PasswordResetMessageRepositoryMongo import PasswordResetMessageRepositoryMongo
from src.mongo_setup import db, client

mongo_repository = PasswordResetMessageRepositoryMongo(
    db, client, settings.mongodb_collection_name
)


def process_message(ch, method, properties, body):
    retry_count = properties.headers.get("x-delivery-count", 0)
    if retry_count >= 5:
        logger.warning(f"Max consecutive retries reached, sending to DLX.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    message_dict = json.loads(body.decode())
    email = properties.headers.get("subject")
    user_id = message_dict["user_id"]
    reset_link = message_dict["reset_link"]
    publishing_datetime = message_dict["publishing_datetime"]

    reset_password_message = PasswordResetMessageSchemaBase(
        email=email,
        user_id=user_id,
        reset_link=reset_link,
        publishing_datetime=publishing_datetime,
    )

    title = "Password reset token"
    body = (
        f"Here is you password reset url, your frontend application should use it in order"
        f"to send request to a password restoration API endpoint: {reset_link}"
    )

    with mongo_repository.add_one(reset_password_message):
        SESService().verify_email(settings.localstack_sender_email)
        SESService().send_email(
            subject=title,
            body=body,
            sender=settings.localstack_sender_email,
            recipients=[email],
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)
