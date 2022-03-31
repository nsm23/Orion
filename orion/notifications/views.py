import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse, reverse_lazy

from complaints.models import Complaint
from .services import (get_notifying_object, generate_response_comments, generate_response_likes,
                       generate_response_moderation_actions, generate_response_posts, generate_response_complaints)
from comments.models import Comment
from likes.models import LikeDislike
from moderation.models import Moderation
from notifications.models import Notification
from posts.models import Post
from users import permission_services

COMMENT_NOTIFICATIONS_NUMBER_TO_SHOW = 3
COMPLAINT_NOTIFICATIONS_NUMBER_TO_SHOW = 3
LIKES_NOTIFICATIONS_NUMBER_TO_SHOW = 3
POST_TO_MODERATOR_NUMBER_TO_SHOW = 3
POST_MODERATION_RESULT_NUMBER_TO_SHOW = 3


@login_required(login_url=reverse_lazy('users:login'))
def get_notifications(request):
    notifications = Notification.objects.filter(
        target_user=request.user,
        status=Notification.NotificationStatus.UNREAD,
    )

    comments = get_notifying_object(notifications, Comment, '-modified_at')
    likes = get_notifying_object(notifications, LikeDislike)
    moderation_actions = get_notifying_object(notifications, Moderation, '-date')
    complaints = get_notifying_object(notifications, Complaint)

    response_notifications = {}
    if permission_services.has_moderator_permissions(request.user):
        post_ids = Notification.objects.filter(
            target_user__isnull=True,
            status=Notification.NotificationStatus.UNREAD,
            content_type__model='post',
        ).values_list('object_id')
        posts_to_moderate = Post.objects.filter(id__in=post_ids)
        response_posts_to_moderate = generate_response_posts(posts_to_moderate,
                                                             POST_TO_MODERATOR_NUMBER_TO_SHOW)
        response_notifications = {
            'posts_to_moderate': response_posts_to_moderate,
            'posts_to_moderate_count': len(post_ids)
        }

    response_comments = generate_response_comments(comments, COMMENT_NOTIFICATIONS_NUMBER_TO_SHOW)
    response_likes = generate_response_likes(likes, LIKES_NOTIFICATIONS_NUMBER_TO_SHOW)
    response_moderation_actions = generate_response_moderation_actions(moderation_actions,
                                                                       POST_TO_MODERATOR_NUMBER_TO_SHOW)
    response_complaints = generate_response_complaints(complaints, COMPLAINT_NOTIFICATIONS_NUMBER_TO_SHOW)

    return JsonResponse(dict({
        'comments': response_comments,
        'likes': response_likes,
        'moderation_acts': response_moderation_actions,
        'complaints': response_complaints,
        'notifications_count': len(comments) + len(likes) + len(moderation_actions) + len(complaints),
        'current_user_id': request.user.id
    }, **response_notifications))


@require_http_methods(["POST"])
@login_required(login_url=reverse_lazy('users:login'))
def mark_as_read(request):
    post_data = json.loads(request.body.decode("utf-8"))
    ids = post_data.get('ids')
    notifications = Notification.objects.filter(object_id__in=ids)
    Notification.mark_notifications_read(notifications)
    return JsonResponse({'ids': ids})


@require_http_methods(["GET"])
@login_required(login_url=reverse_lazy('users:login'))
def mark_as_read_and_redirect(request, object_id, object_model):
    notification = Notification.objects.filter(object_id=object_id, content_type__model=object_model)
    Notification.mark_notifications_read(notification)
    if object_model == 'comment':
        comment = get_object_or_404(Comment, pk=object_id)
        slug = comment.post.slug
        return redirect(reverse('posts:detail', kwargs={'slug': slug}) + f'#comment-{comment.id}')
    if object_model == 'likedislike':
        like = get_object_or_404(LikeDislike, pk=object_id)
        return redirect(reverse('posts:detail', kwargs={'slug': like.content_object.slug}))
    if object_model in ['post', 'complaint']:
        post = get_object_or_404(Post, pk=object_id)
        return redirect(reverse('posts:detail', kwargs={'slug': post.slug}))
    raise Http404
