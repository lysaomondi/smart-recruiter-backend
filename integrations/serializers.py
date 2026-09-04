from rest_framework import serializers

from .models import CodewarsKata


class CodewarsKataSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = CodewarsKata
        fields = [
            "id",
            "kata_id",
            "name",
            "slug",
            "url",
            "description",
            "category",
            "rank_name",
            "rank_slug",
            "languages",
            "tags",
            "total_completed",
            "total_attempted",
            "fetched_at",
            "created_at",
        ]
        read_only_fields = fields