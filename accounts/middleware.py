class UsernameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            
            request.user.__dict__['username'] = request.user.email
        
        response = self.get_response(request)
        return response 