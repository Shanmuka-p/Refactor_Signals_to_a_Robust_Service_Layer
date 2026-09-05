from django.http import JsonResponse

def health_check(request):
    """
    Health check endpoint for Docker Compose healthcheck and load balancers.
    """
    return JsonResponse({"status": "healthy"})
