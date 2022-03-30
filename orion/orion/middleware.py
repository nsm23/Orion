from hub.models import Hub


class HubsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, _, response):
        hubs = Hub.objects.order_by('sort_order')[:4]
        response.context_data['hubs'] = hubs
        return response
