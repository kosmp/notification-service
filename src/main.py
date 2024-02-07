import json

import pika
from pika.credentials import PlainCredentials
from pika.exceptions import AMQPConnectionError, ProbableAuthenticationError
from pymongo.client_session import ClientSession

from src.logging_config import logger
from src.mongo_setup import mongo_repository, client
from src.schemas import PasswordResetMessageSchemaBase
from src.config import settings
from src.aws_service import SESService


def process_message(ch, method, properties, body, mongo_session: ClientSession):
    mongo_session.start_transaction()

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

    mongo_repository.add_one(reset_password_message)

    title = "Password reset token"
    body = (
        f"Here is you password reset url, your frontend application should use it in order"
        f"to send request to a password restoration API endpoint: {reset_link}"
    )

    SESService().verify_email(settings.localstack_sender_email)
    SESService().send_email(
        subject=title,
        body=body,
        sender=settings.localstack_sender_email,
        recipients=[email],
    )

    mongo_session.commit_transaction()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    mongo_session = None
    try:
        credentials = PlainCredentials(
            settings.rabbitmq_default_user, settings.rabbitmq_default_pass
        )

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                settings.rabbitmq_host,
                settings.rabbitmq_port,
                settings.rabbitmq_vhost,
                credentials=credentials,
                heartbeat=0,
            )
        )

        if connection:
            logger.info("Connection to rabbitmq established.")

        channel = connection.channel()
        channel.basic_qos(prefetch_count=3)

        channel.exchange_declare(exchange="email-x", exchange_type="direct")
        channel.exchange_declare(exchange="email-dlx", exchange_type="direct")

        channel.queue_declare(
            queue=settings.rabbitmq_email_queue_name,
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-dead-letter-exchange": "email-dlx",
            },
        )

        channel.queue_declare(
            queue="email-queue-dl",
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-dead-letter-exchange": "email-x",
                "x-message-ttl": 10000,
            },
        )

        channel.queue_bind(exchange="email-x", queue=settings.rabbitmq_email_queue_name)
        channel.queue_bind(exchange="email-dlx", queue="email-queue-dl")

        mongo_session = client.start_session()

        channel.basic_consume(
            queue="reset-password-stream",
            on_message_callback=lambda ch, method, properties, body: process_message(
                ch, method, properties, body, mongo_session
            ),
        )
        logger.info("Start message consuming.")
        channel.start_consuming()
    except ProbableAuthenticationError as err:
        logger.error(
            f"Authentication failed. Please check your username and password. Error message: {err}"
        )
    except AMQPConnectionError as err:
        logger.error(
            f"Connection error. Check the availability of the RabbitMQ server. Error message: {err}"
        )
    except Exception as err:
        if mongo_session:
            mongo_session.abort_transaction()
            client.close()
        logger.error(f"General error: {err}")


if __name__ == "__main__":
    main()
