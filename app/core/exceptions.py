class AppException(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(AppException):  # UNUSED (demo)
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="AUTH_ERROR")


class AuthorizationError(AppException):  # UNUSED (demo)
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, code="FORBIDDEN")


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, code="VALIDATION_ERROR")


class NotFoundError(AppException):
    def __init__(self, entity: str = "Resource"):
        super().__init__(f"{entity} not found", code="NOT_FOUND")


class RateLimitError(AppException):  # UNUSED (demo)
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, code="RATE_LIMITED")


class ExternalServiceError(AppException):  # UNUSED (demo)
    def __init__(self, service: str, message: str = "Service unavailable"):
        self.service = service
        super().__init__(f"{service}: {message}", code="EXTERNAL_ERROR")
