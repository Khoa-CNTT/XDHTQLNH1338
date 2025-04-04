from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/web_01/'):
            # If the user is not authenticated
            if not request.user.is_authenticated:
                # Exclude paths that start with '/api/', '/swagger/', and the login page
                if not request.path.startswith('/api/') and not request.path.startswith('/swagger/') and not request.path.startswith(reverse('web_01:login')):
                    # Redirect to the login page for all non-API and non-Swagger paths
                    return redirect(reverse('web_01:login'))

        # Continue processing the request if authenticated or the path is allowed
        return self.get_response(request)
