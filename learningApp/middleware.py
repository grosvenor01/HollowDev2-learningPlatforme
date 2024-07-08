
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.debug import technical_500_response
logger = logging.getLogger(__name__)

class ErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error('Server error:', exc_info=e)
            return self.handle_500_error(request, e)

        if response.status_code == 404:
            return self.handle_404_error(request)

        return response

    def handle_404_error(self, request):
        return render(request, 'chat/404.html', status=404)

    def handle_500_error(self, request, exception):
        return JsonResponse({
            'message': 'An error occurred on the server',
            'error': 'Something went wrong' if self.get_response.settings.DEBUG else str(exception)
        })