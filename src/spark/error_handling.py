"""
Error handling and retry mechanisms for the Spark AI Video Generation Pipeline.
"""

import asyncio
import logging
import random
import time
from typing import Any, Callable, Dict, Optional, Type
from functools import wraps

from spark.config import RetryConfig


logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API-related errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, retry_after: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded."""
    pass


class VideoGenerationError(APIError):
    """Exception raised when video generation fails."""
    pass


class APIErrorHandler:
    """Handler for API errors with retry logic and exponential backoff."""
    
    def __init__(self, retry_config: RetryConfig):
        self.retry_config = retry_config
        self.logger = logging.getLogger(__name__)
    
    def handle_api_failure(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle API failure and determine if retry should be attempted.
        
        Args:
            error: The exception that occurred
            context: Context information about the failed operation
            
        Returns:
            bool: True if retry should be attempted, False otherwise
        """
        if isinstance(error, RateLimitError):
            self.logger.warning(f"Rate limit exceeded: {error}")
            if error.retry_after:
                self.handle_rate_limiting(error.retry_after)
            return True
        
        if isinstance(error, VideoGenerationError):
            self.logger.error(f"Video generation failed: {error}")
            # Some video generation errors are retryable
            return error.status_code in [500, 502, 503, 504] if error.status_code else True
        
        if isinstance(error, APIError):
            self.logger.error(f"API error: {error}")
            # Retry on server errors, not client errors
            return error.status_code >= 500 if error.status_code else True
        
        # For other exceptions, log and don't retry
        self.logger.error(f"Unexpected error: {error}")
        return False
    
    def implement_exponential_backoff(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            float: Delay in seconds
        """
        if attempt >= self.retry_config.max_retries:
            return 0
        
        # Calculate exponential delay
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1) * delay
        return delay + jitter
    
    def handle_rate_limiting(self, retry_after: int) -> None:
        """
        Handle rate limiting by waiting for the specified time.
        
        Args:
            retry_after: Time to wait in seconds
        """
        wait_time = min(retry_after, self.retry_config.max_delay)
        self.logger.info(f"Rate limited, waiting {wait_time} seconds")
        time.sleep(wait_time)


def retry_with_backoff(
    retry_config: RetryConfig,
    exceptions: tuple = (APIError,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for implementing retry logic with exponential backoff.
    
    Args:
        retry_config: Configuration for retry behavior
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            error_handler = APIErrorHandler(retry_config)
            last_exception = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_retries:
                        logger.error(f"Max retries ({retry_config.max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    if not error_handler.handle_api_failure(e, {"attempt": attempt, "function": func.__name__}):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    delay = error_handler.implement_exponential_backoff(attempt)
                    if delay > 0:
                        logger.info(f"Retrying {func.__name__} in {delay:.2f} seconds (attempt {attempt + 1}/{retry_config.max_retries})")
                        time.sleep(delay)
                    
                    if on_retry:
                        on_retry(attempt, e)
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


async def async_retry_with_backoff(
    retry_config: RetryConfig,
    exceptions: tuple = (APIError,),
    on_retry: Optional[Callable] = None
):
    """
    Async version of retry_with_backoff decorator.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            error_handler = APIErrorHandler(retry_config)
            last_exception = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == retry_config.max_retries:
                        logger.error(f"Max retries ({retry_config.max_retries}) exceeded for {func.__name__}")
                        raise
                    
                    if not error_handler.handle_api_failure(e, {"attempt": attempt, "function": func.__name__}):
                        logger.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    delay = error_handler.implement_exponential_backoff(attempt)
                    if delay > 0:
                        logger.info(f"Retrying {func.__name__} in {delay:.2f} seconds (attempt {attempt + 1}/{retry_config.max_retries})")
                        await asyncio.sleep(delay)
                    
                    if on_retry:
                        await on_retry(attempt, e) if asyncio.iscoroutinefunction(on_retry) else on_retry(attempt, e)
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                    raise
            
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


class GracefulErrorRecovery:
    """Handles graceful error recovery and user notification."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_video_generation_failure(self, prompt: str, error: Exception) -> Optional[str]:
        """
        Handle video generation failure with alternative approaches.
        
        Args:
            prompt: The original video prompt
            error: The error that occurred
            
        Returns:
            Optional[str]: Alternative video path or None if no recovery possible
        """
        self.logger.warning(f"Video generation failed for prompt: {prompt[:50]}...")
        
        # Try alternative approaches
        alternatives = [
            self._try_simplified_prompt,
            self._try_alternative_model,
            self._generate_placeholder_clip
        ]
        
        for alternative in alternatives:
            try:
                result = alternative(prompt, error)
                if result:
                    self.logger.info(f"Recovery successful using {alternative.__name__}")
                    return result
            except Exception as alt_error:
                self.logger.warning(f"Alternative {alternative.__name__} failed: {alt_error}")
        
        self.logger.error(f"All recovery attempts failed for prompt: {prompt[:50]}...")
        return None
    
    def _try_simplified_prompt(self, prompt: str, error: Exception) -> Optional[str]:
        """Try generating with a simplified version of the prompt."""
        # This would implement prompt simplification logic
        # For now, return None to indicate not implemented
        return None
    
    def _try_alternative_model(self, prompt: str, error: Exception) -> Optional[str]:
        """Try generating with an alternative model."""
        # This would implement model switching logic
        # For now, return None to indicate not implemented
        return None
    
    def _generate_placeholder_clip(self, prompt: str, error: Exception) -> Optional[str]:
        """Generate a placeholder clip when all else fails."""
        # This would generate a simple placeholder video
        # For now, return None to indicate not implemented
        return None
    
    def notify_user_of_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Notify user of error with clear message and recovery options.
        
        Args:
            error: The error that occurred
            context: Context information about the error
        """
        error_message = self._format_user_friendly_error(error, context)
        self.logger.info(f"User notification: {error_message}")
        
        # In a real implementation, this would send notifications through
        # the appropriate channels (UI, email, etc.)
        print(f"Error: {error_message}")
    
    def _format_user_friendly_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """Format error message in user-friendly way."""
        if isinstance(error, RateLimitError):
            return "API rate limit exceeded. Please wait a moment and try again."
        
        if isinstance(error, VideoGenerationError):
            return f"Video generation failed: {str(error)}. Trying alternative approaches."
        
        if isinstance(error, APIError):
            return f"Service temporarily unavailable: {str(error)}. Please try again later."
        
        return f"An unexpected error occurred: {str(error)}. Please contact support if the issue persists."