import time
import logging
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("django")


class RequestTimeMiddleware:
    """Middleware to measure and log request processing time."""

    def __init__(self, get_response) -> None:
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request, measure duration, and add custom header."""
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        logger.info(f"Query {request.path} was being processed for {duration:.4f} seconds.")
        response["X-My-Custom-Header"] = "Django-Course-Project"

        return response
