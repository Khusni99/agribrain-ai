class AgriBrainError(Exception):
    status_code: int = 500
    detail: str = "Internal server error"


class NotFoundError(AgriBrainError):
    status_code = 404
    detail = "Resource not found"


class ValidationError(AgriBrainError):
    status_code = 400
    detail = "Validation error"


class AuthenticationError(AgriBrainError):
    status_code = 401
    detail = "Authentication failed"
