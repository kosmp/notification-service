import asyncio
import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, ExchangeType
from aio_pika.exceptions import AMQPConnectionError, ProbableAuthenticationError
from src.logging_config import logger
from src.mongo_setup import client, mongo_repository
from src.schemas import PasswordResetMessageSchemaBase
from src.config import settings
from src.aws_service import SESService


async def process_message(message: AbstractIncomingMessage) -> None:
    async with message.process(ignore_processed=True):
        async with await client.start_session() as session, session.start_transaction():
            retry_count = message.headers.get("x-delivery-count", 0)
            if retry_count >= 5:
                logger.warning(f"Max consecutive retries reached, sending to DLX.")
                await message.nack(requeue=False)
                return

            message_dict = json.loads(message.body.decode())
            email = message.headers.get("subject")
            user_id = message_dict["user_id"]
            reset_link = message_dict["reset_link"]
            publishing_datetime = message_dict["publishing_datetime"]

            reset_password_message = PasswordResetMessageSchemaBase(
                email=email,
                user_id=user_id,
                reset_link=reset_link,
                publishing_datetime=publishing_datetime,
            )

            await mongo_repository.add_one(reset_password_message)

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


async def main() -> None:
    try:
        connection = await aio_pika.connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_default_user,
            password=settings.rabbitmq_default_pass,
            timeout=settings.rabbitmq_default_timeout,
        )

        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=3)

            exchange = await channel.declare_exchange(
                "email-x", type=ExchangeType.DIRECT
            )
            exchange_dlx = await channel.declare_exchange(
                "email-dlx", type=ExchangeType.DIRECT
            )
            queue = await channel.declare_queue(
                "reset-password-stream",
                durable=True,
                arguments={
                    "x-queue-type": "quorum",
                    "x-dead-letter-exchange": "email-dlx",
                },
            )
            queue_dl = await channel.declare_queue(
                "email-queue-dl",
                durable=True,
                arguments={
                    "x-queue-type": "quorum",
                    "x-dead-letter-exchange": "email-x",
                    "x-message-ttl": 10000,
                },
            )
            await queue.bind(exchange)
            await queue_dl.bind(exchange_dlx)

            async with queue.iterator() as q:
                async for message in q:
                    await process_message(await message)
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
    asyncio.run(main())
