from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response.data = {
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down.",
            "retry_after": f"{exc.wait} seconds",
        }
    
    return response