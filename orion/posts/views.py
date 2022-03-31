import os
import hashlib
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from gtts import gTTS
from hitcount.views import HitCountDetailView
from pytils.translit import slugify

from complaints.forms import ComplaintForm
from hub.models import Hub
from likes.models import LikeDislike
from notifications.models import Notification
from posts.models import Post
from complaints.models import Complaint
from users.permission_services import has_common_user_permission


class PostDetailView(HitCountDetailView):
    model = Post
    template_name = 'posts/index.html'
    count_hit = True

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset)
        # only author and staff can see inactive post (draft, on moderation, etc)
        if post.status != 'ACTIVE':
            user = self.request.user
            if user != post.user and not user.is_staff:
                raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments_list'] = self.object.comments.filter(active=True, parent__isnull=True)
        context['likes_count'] = self.object.votes.sum_rating()
        context['complaint_form'] = ComplaintForm
        context.update({'popular_posts': Post.objects.order_by('-hit_count_generic__hits')[:5]})
        if self.request.user != AnonymousUser():
            try:
                context['current_user_like'] = LikeDislike.objects.get(user=self.request.user,
                                                                       content_type__model='post',
                                                                       object_id=self.object.id).vote
            except LikeDislike.DoesNotExist:
                pass
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/post_form.html'
    fields = ['title', 'brief_text', 'text', 'image', 'hub', 'tags']

    def form_valid(self, form):
        self.object = form.save()
        publish = 'publish' in self.request.POST
        if publish and self.request.user.rating >= Post.MIN_USER_RATING_TO_PUBLISH or self.request.user.is_staff:
            action = 'publish'
            self.object.status = Post.ArticleStatus.ACTIVE
            redirect_name, section = 'main', None
        elif publish:
            action = 'moderation'
            self.object.status = Post.ArticleStatus.MODERATION
            redirect_name, section = 'cabinet:user_profile', 'user_moderation_posts'
        else:
            action = 'draft'
            self.object.status = Post.ArticleStatus.DRAFT
            redirect_name, section = 'cabinet:user_profile', 'user_drafts'
        self.object.slug = slugify(self.object.title + str(self.object.id))
        self.object.user = self.request.user
        self.object.save()

        if action == 'publish':
            return HttpResponseRedirect(reverse('main'))
        if action == 'moderation':
            Notification.create_notification(
                content_type=ContentType.objects.get(model='post'),
                object_id=self.object.id,
                user_id=self.request.user.id,
                target_user_id=None,
            )
        return HttpResponseRedirect(reverse(redirect_name, kwargs={'pk': self.request.user.id, 'section': section}))

    def has_permission(self):
        return has_common_user_permission(self.request.user)


# ToDo: check, if post was declined previously !
class PostUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    template_name = 'posts/post_form.html'
    fields = ['title', 'brief_text', 'text', 'image', 'hub', 'status', 'tags']

    def has_permission(self):
        if self.request.user.is_anonymous:
            return False
        post = Post.objects.get(slug=self.kwargs.get('slug'))
        return self.request.user.pk == post.user.pk and has_common_user_permission(self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.title = request.POST['title']
        hub_id = request.POST['hub']
        self.object.hub = Hub.objects.get(id=hub_id)
        self.object.brief_text = request.POST['brief_text']
        self.object.text = request.POST['text']
        publish = 'publish' in request.POST
        if not publish:
            self.object.status = Post.ArticleStatus.DRAFT

        self.object.slug = slugify(self.object.title + str(self.object.id))
        if 'image' in request.FILES:
            post_image = request.FILES['image']
            fs = FileSystemStorage()
            fs.save(post_image.name, post_image)
            self.object.image = post_image.name

        self.object.save()

        if publish:
            return HttpResponseRedirect(reverse('main'))
        return HttpResponseRedirect(reverse('cabinet:user_profile',
                                            kwargs={'pk': self.request.user.id, 'section': 'user_drafts'}))


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('main')
    template_name = 'posts/post_delete.html'

    def has_permission(self):
        if self.request.user.is_anonymous:
            return False
        post = Post.objects.get(slug=self.kwargs.get('slug'))
        if self.request.user.pk != post.user.pk and not self.request.user.is_superuser:
            self.raise_exception = True
            return False
        return True


def text_to_voice_view(request, slug):
    if request.method == 'POST':
        text = request.POST.get('text')
        text = text.replace(u'\xa0', ' ')

        text_hash = hashlib.sha1(text.encode("utf-8")).hexdigest()[-10:]
        path = os.path.join('speech', f'{slug}-{text_hash}.mp3')
        full_path = os.path.join('media', path)

        if not os.path.exists(full_path):
            file = gTTS(text=text, lang='ru', slow=False)
            file.save(full_path)

        return HttpResponse(path)
    return HttpResponse()


class ListTagView(ListView):
    template_name = 'index.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_name'] = Post.tags.get(slug=self.kwargs.get('slug')).name
        context['page_title'] = 'Тэг: ' + self.kwargs.get('slug')
        return context

    def get_queryset(self):
        return Post.objects.filter(Q(status=Post.ArticleStatus.ACTIVE) & Q(tags__slug=self.kwargs.get('slug')))
