from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from .forms import CommentForm, PostForm
from .models import Category, Post, User
from .constants import PAGINATE_COUNT
from .service import get_general_posts_filter
from .mixins import (
    EditContentMixin,
    ValidationMixin,
    RedirectionPostMixin,
    RedirectionProfileMixin,
    PostCreateMixin,
    PostFormMixin,
    PostListMixin,
    PostMixin,
    PostIdCreateMixin,
    CommentFormMixin,
    CommentMixin,
    AddAuthorMixin
)


class PostListView(PostListMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self) -> QuerySet[Any]:
        return get_general_posts_filter()


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().select_related(
            'author',
            'location',
            'category',
        )

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:
            return get_object_or_404(get_general_posts_filter(), pk=post.pk)
        return post

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        )
        return context


class CategoryListView(PostListMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return get_general_posts_filter().filter(category=category)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'],
        )
        return context


class PostCreateView(
    LoginRequiredMixin,
    PostFormMixin,
    PostCreateMixin,
    ValidationMixin,
    RedirectionProfileMixin,
    CreateView,
):
    pass


class PostUpdateView(
    EditContentMixin,
    PostFormMixin,
    PostIdCreateMixin,
    ValidationMixin,
    RedirectionPostMixin,
    UpdateView,
):
    pass


class PostDeleteView(
    EditContentMixin,
    PostMixin,
    PostIdCreateMixin,
    RedirectionProfileMixin,
    DeleteView,
):

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


def query():
    return (Post.objects
            .select_related('author', 'location', 'category')
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
            )


class ProfilePostListView(AddAuthorMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        is_author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user == is_author:
            queryset = (query()
                        .filter(author=is_author))
        else:
            queryset = (query()
                        .filter(author=is_author,
                                is_published=True,
                                category__is_published=True,
                                pub_date__lt=timezone.now()))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class EditProfileUpdateView(
    LoginRequiredMixin,
    RedirectionProfileMixin,
    UpdateView,
):
    model = User
    template_name = 'blog/user.html'
    fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    def get_object(self, queryset=None):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, CommentFormMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            get_general_posts_filter(),
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateView(
    EditContentMixin,
    CommentFormMixin,
    UpdateView,
    LoginRequiredMixin
):
    pass


class CommentDeleteView(
    EditContentMixin,
    CommentMixin,
    DeleteView,
    LoginRequiredMixin
):
    pass
