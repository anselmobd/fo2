class VirtualHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if 'agator' in host:
            request.urlconf = 'fo2.urls_agator'
        response = self.get_response(request)
        return response