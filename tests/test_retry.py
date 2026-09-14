import pytest

from utils.retry import retry


def test_retry_succeeds_without_retry():
    calls = []

    def operation():
        calls.append(1)
        return "success"

    result = retry(
        operation,
        retries=3,
        delay=0,
    )

    assert result == "success"
    assert len(calls) == 1


def test_retry_succeeds_after_temporary_failures():
    calls = []

    def operation():
        calls.append(1)

        if len(calls) < 3:
            raise TimeoutError("temporary failure")

        return "success"

    result = retry(
        operation,
        retries=3,
        delay=0,
        exceptions=(TimeoutError,),
    )

    assert result == "success"
    assert len(calls) == 3


def test_retry_raises_after_all_attempts_fail():
    calls = []

    def operation():
        calls.append(1)
        raise TimeoutError("persistent failure")

    with pytest.raises(TimeoutError):
        retry(
            operation,
            retries=3,
            delay=0,
            exceptions=(TimeoutError,),
        )

    assert len(calls) == 4


def test_non_retryable_exception_is_raised_immediately():
    calls = []

    def operation():
        calls.append(1)
        raise ValueError("invalid data")

    with pytest.raises(ValueError):
        retry(
            operation,
            retries=3,
            delay=0,
            exceptions=(TimeoutError,),
        )

    assert len(calls) == 1


def test_negative_retries_are_rejected():
    with pytest.raises(ValueError):
        retry(
            lambda: "success",
            retries=-1,
            delay=0,
        )


def test_negative_delay_is_rejected():
    with pytest.raises(ValueError):
        retry(
            lambda: "success",
            retries=3,
            delay=-1,
        )