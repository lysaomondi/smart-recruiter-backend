from django.db import models


class CodewarsKata(models.Model):
    id = models.BigAutoField(primary_key=True)

    kata_id = models.CharField(
        max_length=100,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
    )

    slug = models.CharField(
        max_length=255,
        blank=True,
    )

    url = models.URLField(
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    category = models.CharField(
        max_length=100,
        blank=True,
    )

    rank_name = models.CharField(
        max_length=100,
        blank=True,
    )

    rank_slug = models.CharField(
        max_length=100,
        blank=True,
    )

    languages = models.JSONField(
        default=list,
        blank=True,
    )

    tags = models.JSONField(
        default=list,
        blank=True,
    )

    total_completed = models.PositiveIntegerField(
        default=0,
    )

    total_attempted = models.PositiveIntegerField(
        default=0,
    )

    fetched_at = models.DateTimeField(
        auto_now=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name