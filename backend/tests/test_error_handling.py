"""
Tests for error handling and retry mechanisms.
"""

import pytest
import time
from unittest.mock import Mock, patch
from spark.error_handling import (
    APIError, RateLimitError, VideoGenerationError,
    APIErrorHandler, retry_with_backoff, GracefulErrorRecovery
)
from spark.config import RetryConfig


def test_api_error_creation():
    """Test APIError exception creation."""
    error = APIError("Test error", status_code=500, retry_after=30)
    
    assert str(error) == "Test error"
    assert error.status_code == 500
    assert error.retry_after == 30


def test_rate_limit_error_creation():
    """Test RateLimitError exception creation."""
    error = RateLimitError("Rate limit exceeded", status_code=429, retry_after=60)
    
    assert str(error) == "Rate limit exceeded"
    assert error.status_code == 429
    assert error.retry_after == 60


def test_video_generation_error_creation():
    """Test VideoGenerationError exception creation."""
    error = VideoGenerationError("Video generation failed", status_code=503)
    
    assert str(error) == "Video generation failed"
    assert error.status_code == 503


def test_api_error_handler_creation():
    """Test APIErrorHandler creation."""
    retry_config = RetryConfig(max_retries=3, base_delay=1.0)
    handler = APIErrorHandler(retry_config)
    
    assert handler.retry_config == retry_config
    assert handler.retry_config.max_retries == 3


def test_api_error_handler_rate_limit():
    """Test APIErrorHandler handling of rate limit errors."""
    retry_config = RetryConfig(max_retries=3, base_delay=0.1, max_delay=1.0)
    handler = APIErrorHandler(retry_config)
    
    error = RateLimitError("Rate limited", retry_after=1)
    context = {"attempt": 1}
    
    # Should return True for retry
    should_retry = handler.handle_api_failure(error, context)
    assert should_retry is True


def test_api_error_handler_video_generation_error():
    """Test APIErrorHandler handling of video generation errors."""
    retry_config = RetryConfig(max_retries=3)
    handler = APIErrorHandler(retry_config)
    
    # Server error - should retry
    server_error = VideoGenerationError("Server error", status_code=500)
    should_retry = handler.handle_api_failure(server_error, {})
    assert should_retry is True
    
    # Client error - should not retry
    client_error = VideoGenerationError("Bad request", status_code=400)
    should_retry = handler.handle_api_failure(client_error, {})
    assert should_retry is False


def test_exponential_backoff_calculation():
    """Test exponential backoff delay calculation."""
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0,
        exponential_base=2.0
    )
    handler = APIErrorHandler(retry_config)
    
    # Test delay progression
    delay_0 = handler.implement_exponential_backoff(0)
    delay_1 = handler.implement_exponential_backoff(1)
    delay_2 = handler.implement_exponential_backoff(2)
    
    # Should increase exponentially (with jitter)
    assert 1.0 <= delay_0 <= 1.1  # base_delay + jitter
    assert 2.0 <= delay_1 <= 2.2  # base_delay * 2 + jitter
    assert 4.0 <= delay_2 <= 4.4  # base_delay * 4 + jitter
    
    # Test max delay cap
    delay_high = handler.implement_exponential_backoff(10)
    assert delay_high <= retry_config.max_delay * 1.1  # max_delay + jitter


def test_retry_decorator_success():
    """Test retry decorator with successful function."""
    retry_config = RetryConfig(max_retries=3, base_delay=0.01)
    
    @retry_with_backoff(retry_config)
    def successful_function():
        return "success"
    
    result = successful_function()
    assert result == "success"


def test_retry_decorator_with_retryable_error():
    """Test retry decorator with retryable error that eventually succeeds."""
    retry_config = RetryConfig(max_retries=3, base_delay=0.01)
    
    call_count = 0
    
    @retry_with_backoff(retry_config, exceptions=(APIError,))
    def function_with_retryable_error():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise APIError("Temporary error", status_code=500)
        return "success"
    
    result = function_with_retryable_error()
    assert result == "success"
    assert call_count == 3


def test_retry_decorator_max_retries_exceeded():
    """Test retry decorator when max retries are exceeded."""
    retry_config = RetryConfig(max_retries=2, base_delay=0.01)
    
    @retry_with_backoff(retry_config, exceptions=(APIError,))
    def always_failing_function():
        raise APIError("Persistent error", status_code=500)
    
    with pytest.raises(APIError) as exc_info:
        always_failing_function()
    
    assert "Persistent error" in str(exc_info.value)


def test_retry_decorator_non_retryable_error():
    """Test retry decorator with non-retryable error."""
    retry_config = RetryConfig(max_retries=3, base_delay=0.01)
    
    @retry_with_backoff(retry_config, exceptions=(APIError,))
    def function_with_non_retryable_error():
        raise ValueError("Non-retryable error")
    
    with pytest.raises(ValueError) as exc_info:
        function_with_non_retryable_error()
    
    assert "Non-retryable error" in str(exc_info.value)


def test_graceful_error_recovery_creation():
    """Test GracefulErrorRecovery creation."""
    recovery = GracefulErrorRecovery()
    assert recovery is not None


def test_graceful_error_recovery_video_generation_failure():
    """Test graceful error recovery for video generation failure."""
    recovery = GracefulErrorRecovery()
    
    prompt = "Test video prompt"
    error = VideoGenerationError("Generation failed")
    
    # Currently returns None as alternatives are not implemented
    result = recovery.handle_video_generation_failure(prompt, error)
    assert result is None


def test_graceful_error_recovery_user_notification():
    """Test user notification formatting."""
    recovery = GracefulErrorRecovery()
    
    # Test different error types
    rate_limit_error = RateLimitError("Rate limit exceeded")
    video_error = VideoGenerationError("Video generation failed")
    api_error = APIError("Service unavailable")
    generic_error = Exception("Unknown error")
    
    # Test that notification doesn't raise exceptions
    recovery.notify_user_of_error(rate_limit_error, {})
    recovery.notify_user_of_error(video_error, {})
    recovery.notify_user_of_error(api_error, {})
    recovery.notify_user_of_error(generic_error, {})


def test_error_message_formatting():
    """Test user-friendly error message formatting."""
    recovery = GracefulErrorRecovery()
    
    # Test rate limit error
    rate_error = RateLimitError("Rate limit exceeded")
    message = recovery._format_user_friendly_error(rate_error, {})
    assert "rate limit" in message.lower()
    
    # Test video generation error
    video_error = VideoGenerationError("Video failed")
    message = recovery._format_user_friendly_error(video_error, {})
    assert "video generation failed" in message.lower()
    
    # Test API error
    api_error = APIError("Service down")
    message = recovery._format_user_friendly_error(api_error, {})
    assert "service temporarily unavailable" in message.lower()
    
    # Test generic error
    generic_error = Exception("Unknown issue")
    message = recovery._format_user_friendly_error(generic_error, {})
    assert "unexpected error" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__])