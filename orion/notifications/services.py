from typing import Any, Dict, List, Type, Union
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet
from django.utils import dateformat, timezone

from .models import Notification


def generate_response_comments(comments, limit: int) -> List[Dict[str, Any]]:
    return [{
        'user_id': comment.user.id,
        'username': comment.user.username,
        'user_avatar_url': comment.user.avatar.url,
        'post_id': comment.post.id,
        'text': comment.text,
        'created_at': format_datetime_with_system_timezone(comment.created_at, 'd.m.Y H:i'),
        'comment_id': comment.id,
    } for comment in comments[:limit]]


def generate_response_likes(likes, limit: int) -> List[Dict[str, Any]]:
    return [{
        'user_id': like.user.id,
        'username': like.user.username,
        'user_avatar_url': like.user.avatar.url,
        'like_id': like.id,
        'vote': like.vote,
        'post_id': like.object_id,
        'post_title': like.content_object.title,
    } for like in likes[:limit]]


def generate_response_moderation_actions(moderation_actions, limit: int) -> List[Dict[str, Any]]:
    return [{
        'object_id': mod.object_id,
        'content_type': mod.content_type.model,
        'decision': mod.decision,
        'comment': mod.comment,
        'text': mod.content_object.title if mod.content_type.model == 'post' else '',
    } for mod in moderation_actions[:limit]]


def generate_response_posts(posts, limit: int) -> List[Dict[str, Any]]:
    return [{
        'post_id': post.id,
        'post_slug': post.slug,
        'post_title': post.title,
        'post_user_id': post.user.id,
        'username': post.user.username,
        'user_avatar_url': post.user.avatar.url,
    } for post in posts[:limit]]


def get_notifying_object(notifications: Union[QuerySet, List[Notification]],
                         model: Type[Model],
                         order_by: Union[str, None] = None) -> QuerySet:
    object_ids = notifications.filter(content_type__model=model.__name__.lower()).values_list('object_id')
    queryset = model.objects.filter(id__in=object_ids)
    if order_by:
        queryset = queryset.order_by(order_by)
    return queryset


def set_notifications_status_as_read(notifications: Union[QuerySet, List[Notification]]) -> None:
    for notification in notifications:
        notification.status = Notification.NotificationStatus.READ
    Notification.objects.bulk_update(notifications, ['status'])


def get_unread_post_notifications(post_id: int) -> QuerySet:
    return Notification.objects.filter(
        content_type=ContentType.objects.get(model='post'),
        object_id=post_id,
        status=Notification.NotificationStatus.UNREAD,
    )


def format_datetime_with_system_timezone(dt: datetime, dt_format: str) -> str:
    return dateformat.format(
        value=timezone.localtime(dt, timezone.get_current_timezone()),
        format_string=dt_format,
    )
