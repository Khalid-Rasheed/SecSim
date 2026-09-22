"""Service-layer errors: domain failures with an HTTP status attached.

Services raise these instead of returning Flask responses, which keeps
business logic framework-free and unit-testable. Routes translate them
with a single ``except ServiceError`` clause.
"""


class ServiceError(Exception):
    """A domain failure meant for the API client.

    Attributes:
        message: Client-safe error text (no internals, no stack traces).
        status: HTTP status code the route should answer with.
    """

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status
