from django.shortcuts import get_object_or_404

from .models import Post


def post_status_update(post_id: int, status: Post.ArticleStatus) -> Post:
    post = get_object_or_404(Post, id=post_id)
    post.status = status
    post.save()
    return post
