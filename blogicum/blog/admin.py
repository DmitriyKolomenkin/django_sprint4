from django.contrib import admin

from .models import Post, Category, Location

# admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)


class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'is_published',
        'created_at',
        'pub_date',
    )

    list_editable = (
        'is_published',
        'pub_date',
    )

    search_fields = [
        'title',
        'caregory__title',
        'location__name',
        'category__slug',
    ]

    list_filter = (
        'id',
        'is_published',
        'created_at',
        'pub_date',
    )


admin.site.register(Post, BlogAdmin)
