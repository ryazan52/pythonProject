from django.core.cache import cache
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm, ProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import datetime
from .tasks import printing, hello
from django.http import HttpResponse

import logging

logger = logging.getLogger(__name__)


class PostsList(ListView):
    model = Post
    ordering = '-post_datetime'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostSearch(ListView):
    model = Post
    ordering = '-post_datetime'
    template_name = 'post_search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    model = User
    template_name = 'profile_update.html'
    success_url = reverse_lazy('post_list')


class CategoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.post_category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(post_category=self.post_category).order_by('-post_datetime')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.post_category.subscribers.all()
        context['post_category'] = self.post_category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = 'You are subscribed on'
    return render(request, 'subscribe.html', {'category': category, 'message': message})


def send_notifications(preview, pk, title, subscribers):
    """Sending notification to all subscribers"""
    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': preview,
            'link': f'{settings.SITE_URL}/posts/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def mailing_to_subs():
    """Sending weekly list of news"""
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(post_datetime__gte=last_week)
    categories = set(posts.values_list('post_category__category_name', flat=True))
    subscribers = set(
        Category.objects.filter(category_name__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': f'{settings.SITE_URL}/posts/',
            'posts': posts,
        }
    )
    msg = EmailMultiAlternatives(
        subject='Articles for the last week',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


class IndexView(View):
    def get(self, request):
        printing.delay(10)
        hello.delay()
        return HttpResponse('Hi!')
