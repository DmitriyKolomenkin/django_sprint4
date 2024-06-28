from typing import Any

from django.db.models import Count
from django.utils import timezone
from django.db.models.query import QuerySet

from .models import Post


def get_general_posts_filter() -> QuerySet[Any]:
    return Post.objects.select_related(
        'author',
        'location',
        'category',
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
