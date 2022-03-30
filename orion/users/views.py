from django.contrib import auth
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView, UpdateView
from django.urls import reverse, reverse_lazy

from comments.models import Comment
from likes.models import LikeDislike
from moderation.models import Moderation
from notifications.models import Notification
from posts.models import Post
from users.models import User
from users.forms import UserForm, RegisterForm
from users.permission_services import has_common_user_permission


class UserLoginView(LoginView):
    template_name = 'users/user_login.html'
    form_class = AuthenticationForm
    next_page = reverse_lazy('main')


def register(request):
    if request.method == 'POST':
        form_reg = RegisterForm(request.POST)
        if form_reg.is_valid():
            user = form_reg.save(commit=False)
            user.set_password(form_reg.cleaned_data['password'])
            user.save()
            return render(request, 'users/user_reg_done.html', {'user': user})
    else:
        form_reg = RegisterForm()
    return render(request, 'users/user_register.html', {'form_reg': form_reg})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse_lazy('main'))


class UserProfileView(PermissionRequiredMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'users/user_profile.html'
    slug_field = 'username'
    login_url = reverse_lazy('users:login')

    INSECURE_SECTIONS = ['user_detail', 'user_posts']

    def get_context_data(self, **kwargs):
        user = kwargs.get('object')
        section = self.kwargs.get('section', 'user_detail')
        if section == 'user_posts':
            kwargs['posts'] = user.posts.filter(status=Post.ArticleStatus.ACTIVE)
        elif section == 'user_drafts':
            kwargs['posts'] = user.posts.filter(status=Post.ArticleStatus.DRAFT)
        elif section == 'user_moderation_posts':
            kwargs['posts'] = user.posts.filter(status=Post.ArticleStatus.MODERATION)
        elif section == 'user_moderation_declined_posts':
            posts = user.posts.filter(status=Post.ArticleStatus.DECLINED)
            moderations = Moderation.objects.filter(object_id__in=posts.values_list('id'),
                                                    content_type=ContentType.objects.get(model='post'),
                                                    decision=Moderation.ModerationDecision.DECLINE)

            decline_reasons = {m.object_id: m.comment for m in moderations}
            kwargs['posts'] = [{'object': post, 'decline_reason': decline_reasons.get(post.id)} for post in posts]

        elif section == 'user_comment_notifications':
            notifications = Notification.objects.filter(target_user=user)

            read_comment_ids = (notifications
                                .filter(content_type__model='comment', status=Notification.NotificationStatus.READ)
                                .values_list('object_id'))
            unread_comment_ids = (notifications
                                  .filter(content_type__model='comment', status=Notification.NotificationStatus.UNREAD)
                                  .values_list('object_id'))
            read_comments = Comment.objects.filter(id__in=read_comment_ids)
            unread_comments = Comment.objects.filter(id__in=unread_comment_ids)

            kwargs['read_comments'] = read_comments
            kwargs['unread_comments'] = unread_comments
        elif section == 'user_like_notifications':
            notifications = Notification.objects.filter(target_user=user)
            read_like_ids = (notifications
                             .filter(content_type__model='likedislike', status=Notification.NotificationStatus.READ)
                             .values_list('object_id'))
            unread_like_ids = (notifications
                               .filter(content_type__model='likedislike', status=Notification.NotificationStatus.UNREAD)
                               .values_list('object_id'))

            read_likes = LikeDislike.objects.filter(id__in=read_like_ids)
            unread_likes = LikeDislike.objects.filter(id__in=unread_like_ids)

            kwargs['read_likes'] = read_likes
            kwargs['unread_likes'] = unread_likes
        kwargs['section'] = section

        return super().get_context_data(**kwargs)

    def has_permission(self):
        section = self.kwargs.get('section', 'user_detail')
        if section in self.INSECURE_SECTIONS:
            return True
        return has_common_user_permission(self.request.user) and self.request.user.pk == self.kwargs["pk"]


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name_suffix = '_update_form'
    permission_required = 'users.can_update'
    login_url = reverse_lazy('users:login')

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('users:user_profile', kwargs={'pk': pk, 'section': 'user_detail'})

    def has_permission(self):
        if self.request.user.is_anonymous:
            return False
        if self.request.user.pk != self.kwargs['pk'] and not self.request.user.is_superuser:
            self.raise_exception = True
            return False
        return True


def set_status(request, pk, status):
    if request.user.is_superuser:
        user = User.objects.get(pk=pk)
        user.is_staff = True if status == 'moderator' else False
        user.save()
    return HttpResponseRedirect(reverse('users:user_detail', kwargs={'pk': pk}))
