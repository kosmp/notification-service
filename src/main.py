import asyncio

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, ExchangeType
from aio_pika.exceptions import AMQPConnectionError, ProbableAuthenticationError
from src.config import settings
from src.logging_config import logger


async def process_message(message: AbstractIncomingMessage) -> None:
    pass


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
                "email-x", type=ExchangeType.FANOUT
            )
            exchange_dlx = await channel.declare_exchange(
                "email-dlx", type=ExchangeType.FANOUT
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
