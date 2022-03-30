import operator
from functools import reduce
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.db.models import Q

from posts.models import Post
from hub.models import Hub


class HubView(ListView):
    template_name = 'hub/index.html'
    paginate_by = 12

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        hub = get_object_or_404(Hub, alias=slug)
        self.extra_context = {
            'page_title': f'Хаб | {hub}',
            'current_hub': slug,
        }
        return Post.objects.filter(Q(hub__alias=slug) & Q(status=Post.ArticleStatus.ACTIVE))


class MainView(ListView):
    template_name = 'index.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'search_keys'):
            search_fields = ', '.join(self.search_keys)
            context['search_field'] = search_fields
            context['page_title'] = 'Поиск по ключевым словам' + search_fields
        else:
            context['page_title'] = 'Главная'
        return context

    def get_queryset(self):
        search_string = self.request.GET.get('search')
        if search_string:
            self.search_keys = search_string.strip().split()
            return Post.objects.filter(
                Q(status=Post.ArticleStatus.ACTIVE) & (
                    reduce(operator.or_, (Q(title__icontains=x) for x in self.search_keys)) |
                    reduce(operator.or_, (Q(brief_text__icontains=x) for x in self.search_keys)) |
                    reduce(operator.or_, (Q(text__icontains=x) for x in self.search_keys)) |
                    reduce(operator.or_, (Q(user__username__icontains=x) for x in self.search_keys))
                )
            )
        else:
            self.search_keys = ''
            return Post.objects.filter(Q(status=Post.ArticleStatus.ACTIVE))
