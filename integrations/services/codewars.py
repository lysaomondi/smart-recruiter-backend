import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.utils import timezone

from ..models import CodewarsKata


CODEWARS_API_BASE_URL = (
    "https://www.codewars.com/api/v1"
)


class CodewarsAPIError(Exception):
    """Raised when the Codewars API cannot be reached or fails."""


def _request_codewars(endpoint):
    """
    Make a GET request to the Codewars API.
    """

    url = f"{CODEWARS_API_BASE_URL}/{endpoint}"

    request = Request(
        url,
        headers={
            "User-Agent": "SmartRecruiter/1.0",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=10,
        ) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as exc:
        if exc.code == 404:
            raise CodewarsAPIError(
                "Codewars kata was not found."
            ) from exc

        raise CodewarsAPIError(
            f"Codewars API returned HTTP {exc.code}."
        ) from exc

    except URLError as exc:
        raise CodewarsAPIError(
            "Unable to connect to Codewars."
        ) from exc

    except json.JSONDecodeError as exc:
        raise CodewarsAPIError(
            "Codewars returned invalid JSON."
        ) from exc


def get_kata(kata_id_or_slug):
    """
    Retrieve a kata from the Codewars API.

    The Codewars API accepts either a kata ID or slug.
    """

    if not kata_id_or_slug:
        raise CodewarsAPIError(
            "A Codewars kata ID or slug is required."
        )

    return _request_codewars(
        f"code-challenges/{kata_id_or_slug}"
    )


def save_kata(kata_data):
    """
    Save or update Codewars kata metadata
    in the local database.
    """

    kata_id = kata_data.get("id")

    if not kata_id:
        raise CodewarsAPIError(
            "Codewars response did not contain a kata ID."
        )

    rank = kata_data.get("rank") or {}

    kata, created = CodewarsKata.objects.update_or_create(
        kata_id=kata_id,
        defaults={
            "name": kata_data.get(
                "name",
                "",
            ),
            "slug": kata_data.get(
                "slug",
                "",
            ),
            "url": kata_data.get(
                "url",
                "",
            ),
            "description": kata_data.get(
                "description",
                "",
            ),
            "category": kata_data.get(
                "category",
                "",
            ),
            "rank_name": rank.get(
                "name",
                "",
            ),
            "rank_slug": rank.get(
                "slug",
                "",
            ),
            "languages": kata_data.get(
                "languages",
                [],
            ),
            "tags": kata_data.get(
                "tags",
                [],
            ),
            "total_completed": kata_data.get(
                "totalCompleted",
                0,
            ),
            "total_attempted": kata_data.get(
                "totalAttempts",
                0,
            ),
            "fetched_at": timezone.now(),
        },
    )

    return kata, created


def search_kata(query):
    """
    Look up a Codewars kata using its ID or slug
    and cache the result locally.
    """

    kata_data = get_kata(query)

    kata, created = save_kata(kata_data)

    return kata, created