import time

from utils.logger import get_logger


logger = get_logger(__name__)


def retry(
    operation,
    retries=3,
    delay=2,
    exceptions=(Exception,),
):
    """
    Execute an operation with limited retries.

    Args:
        operation: Callable with no arguments.
        retries: Maximum number of retry attempts after the first try.
        delay: Delay in seconds between attempts.
        exceptions: Exceptions that are eligible for retry.

    Returns:
        Result returned by operation().

    Raises:
        Exception:
            The last eligible exception if all attempts fail.
        Exception:
            Any non-eligible exception immediately.
    """

    if retries < 0:
        raise ValueError("retries must be greater than or equal to zero.")

    if delay < 0:
        raise ValueError("delay must be greater than or equal to zero.")

    attempt = 0

    while True:
        try:
            return operation()

        except exceptions as error:
            if attempt >= retries:
                logger.error(
                    "Operation failed after %s attempts | error=%s",
                    attempt + 1,
                    error,
                )
                raise

            attempt += 1

            logger.warning(
                "Operation failed | retry=%s/%s | error=%s",
                attempt,
                retries,
                error,
            )

            if delay > 0:
                time.sleep(delay)