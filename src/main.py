from pika.exceptions import AMQPConnectionError, ProbableAuthenticationError

from src.consumer import connect_and_start_consuming
from src.logging_config import logger


def main() -> None:
    try:
        connect_and_start_consuming()
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
