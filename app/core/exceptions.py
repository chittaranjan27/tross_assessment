from fastapi import status


class AppException(Exception):
    """Base application exception"""

    def __init__(
        self,
        message: str,
        code: str,
        http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(self.message)


class InvalidProfileUrlError(AppException):
    def __init__(
        self, message: str = "The provided URL is not a valid LinkedIn profile URL."
    ):
        super().__init__(message, "INVALID_PROFILE_URL", status.HTTP_400_BAD_REQUEST)


class ProfileNotFoundError(AppException):
    def __init__(
        self,
        message: str = "The requested profile could not be found or is unavailable.",
    ):
        super().__init__(message, "PROFILE_NOT_FOUND", status.HTTP_404_NOT_FOUND)


class UpstreamAuthenticationError(AppException):
    def __init__(
        self, message: str = "Failed to authenticate with the upstream provider."
    ):
        super().__init__(message, "UPSTREAM_AUTH_ERROR", status.HTTP_502_BAD_GATEWAY)


class UpstreamRateLimitError(AppException):
    def __init__(self, message: str = "Upstream provider rate limit exceeded."):
        super().__init__(message, "UPSTREAM_RATE_LIMIT", status.HTTP_502_BAD_GATEWAY)


class UpstreamTimeoutError(AppException):
    def __init__(self, message: str = "Request to the upstream provider timed out."):
        super().__init__(message, "UPSTREAM_TIMEOUT", status.HTTP_504_GATEWAY_TIMEOUT)


class UpstreamUnavailableError(AppException):
    def __init__(self, message: str = "Upstream provider is temporarily unavailable."):
        super().__init__(message, "UPSTREAM_UNAVAILABLE", status.HTTP_502_BAD_GATEWAY)


class UpstreamResponseParseError(AppException):
    def __init__(
        self, message: str = "Failed to parse the response from the upstream provider."
    ):
        super().__init__(message, "UPSTREAM_PARSE_ERROR", status.HTTP_502_BAD_GATEWAY)


class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(
            message, "RATE_LIMIT_EXCEEDED", status.HTTP_429_TOO_MANY_REQUESTS
        )
