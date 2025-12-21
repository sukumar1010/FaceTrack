from rest_framework.views import exception_handler
from django.http import Http404

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get("request")

    if response and response.status_code in (401, 403):
        # Hide API from browser
        raise Http404

    return response
