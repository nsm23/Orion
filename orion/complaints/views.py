from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import CreateView

from complaints.forms import ComplaintForm
from complaints.models import Complaint
from notifications.models import Notification
from posts.models import Post


class JsonableResponseMixin:
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.is_ajax(request=self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        form.instance.user = self.request.user
        if self.is_ajax(request=self.request) and self.request.method == "POST":

            self.object = Complaint(
                user=self.request.user,
                text=form.data.get('text'),
                content_type=ContentType.objects.get(model='post'),
                object_id=form.data.get('post'),
            )
            self.object.save()
            target_user_id = Post.objects.get(pk=self.object.object_id).user.id
            Notification().create_notification(
                content_type=ContentType.objects.get(model='complaint'),
                object_id=self.object.id,
                user_id=self.request.user.id,
                target_user_id=target_user_id,
            )

            data = {
                'status': 200,
                'data': 'Ваша жалоба успешно принята',
            }

            return JsonResponse(data)
        else:
            response = super(JsonableResponseMixin, self).form_valid(form)
            return response

    def is_ajax(self, request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class ComplaintCreateView(JsonableResponseMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
