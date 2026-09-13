from pathlib import Path

from utils.logger import get_logger, LOG_FILE


def test_get_logger_returns_logger():
    logger = get_logger("test_logger")

    assert logger.name == "test_logger"


def test_logger_has_console_and_file_handlers():
    logger = get_logger("test_handlers")

    handler_types = {
        type(handler).__name__
        for handler in logger.handlers
    }

    assert "StreamHandler" in handler_types
    assert "FileHandler" in handler_types


def test_logger_creates_log_file():
    logger = get_logger("test_file")

    logger.info("Test log message")

    assert isinstance(LOG_FILE, Path)
    assert LOG_FILE.exists()


def test_logger_writes_message_to_file():
    logger = get_logger("test_message")

    unique_message = "LOGGER_TEST_MESSAGE_12345"
    logger.info(unique_message)

    content = LOG_FILE.read_text(encoding="utf-8")

    assert unique_message in content