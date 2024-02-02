import asyncio
import aio_pika
from aio_pika.exceptions import AMQPConnectionError, ProbableAuthenticationError
from src.config import settings
from src.logging_config import logger


async def main() -> None:
    try:
        connection = await aio_pika.connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_default_user,
            password=settings.rabbitmq_default_pass,
        )

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=3)
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
