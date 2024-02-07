import pika
from pika.credentials import PlainCredentials
from pika.exceptions import AMQPConnectionError, ProbableAuthenticationError

from src.logging_config import logger
from src.config import settings
from src.process_message_service import process_message


def main() -> None:
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
                "x-dead-letter-routing-key": settings.rabbitmq_email_queue_name,
            },
        )

        channel.queue_declare(
            queue="email-queue-dl",
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-dead-letter-exchange": "email-x",
                "x-dead-letter-routing-key": settings.rabbitmq_email_queue_name,
                "x-message-ttl": settings.rabbitmq_dead_letter_message_ttl,
            },
        )

        channel.queue_bind(
            exchange="email-x",
            queue=settings.rabbitmq_email_queue_name,
            routing_key=settings.rabbitmq_email_queue_name,
        )
        channel.queue_bind(
            exchange="email-dlx",
            queue="email-queue-dl",
            routing_key=settings.rabbitmq_email_queue_name,
        )

        channel.basic_consume(
            queue=settings.rabbitmq_email_queue_name,
            on_message_callback=lambda ch, method, properties, body: process_message(
                ch, method, properties, body
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
        logger.error(f"General error: {err}")


if __name__ == "__main__":
    main()
