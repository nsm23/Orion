from django.db import models
from django.conf import settings
from posts.models import Post


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name="Автор")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Пост")
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="Родительский комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Дата редактирования")

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return 'Comment by {}'.format(self.user.username)
