from django.contrib import admin

from .models import CodewarsKata


@admin.register(CodewarsKata)
class CodewarsKataAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "kata_id",
        "category",
        "rank_name",
        "fetched_at",
    )

    search_fields = (
        "name",
        "kata_id",
        "slug",
    )

    list_filter = (
        "category",
        "rank_name",
    )