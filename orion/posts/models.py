from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hub.models import Hub
from django.utils.translation import gettext_lazy as _
from likes.models import LikeDislike
from users.models import User
from taggit.managers import TaggableManager

from taggit.models import Tag, TaggedItem
from pytils.translit import slugify

from hitcount.models import HitCount


class RuTag(Tag):
    class Meta:
        proxy = True

    def slugify(self, tag, i=None):
        return slugify(self.name)


class RuTaggedItem(TaggedItem):
    class Meta:
        proxy = True

    @classmethod
    def tag_model(cls):
        return RuTag


class Post(models.Model):

    class ArticleStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('DRAFT'),
        ACTIVE = 'ACTIVE', _('ACTIVE'),
        MODERATION = 'ON MODERATION', _('ON MODERATION')
        DECLINED = 'DECLINED', _('DECLINED')
        DELETED = 'DELETED', _('DELETED')
        BANNED = 'BANNED', _('BANNED')

    MIN_USER_RATING_TO_PUBLISH = 7

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(verbose_name='Элиас для урла', max_length=200)
    text = models.TextField(verbose_name='Полный текст')
    brief_text = models.TextField(verbose_name='Сокращенный текст для списков')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='posts', verbose_name='Автор')
    hub = models.ForeignKey(Hub, null=True, blank=True, on_delete=models.SET_NULL, related_name='posts', verbose_name='Хаб')
    image = models.ImageField(upload_to='posts', null=True, blank=True, verbose_name='Картинка поста')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    modified_at = models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')
    status = models.CharField(choices=ArticleStatus.choices, max_length=16, default=ArticleStatus.ACTIVE)
    votes = GenericRelation(LikeDislike, related_query_name='posts')
    tags = TaggableManager(blank=True, through=RuTaggedItem)
    hit_count_generic = GenericRelation(HitCount,
                                        object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')

    def __str__(self):
        return self.title
        
    class Meta:
        ordering = ('-created_at',)

