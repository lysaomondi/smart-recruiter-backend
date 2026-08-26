from unittest.mock import patch

from django.test import TestCase

from .models import CodewarsKata
from .services.codewars import (
    CodewarsAPIError,
    get_kata,
    save_kata,
    search_kata,
)


class CodewarsModelTests(TestCase):
    def test_create_kata(self):
        kata = CodewarsKata.objects.create(
            kata_id="abc123",
            name="Multiply",
            slug="multiply",
            url="https://www.codewars.com/kata/abc123",
            description="Multiply two numbers.",
            category="reference",
            rank_name="8 kyu",
            rank_slug="8-kyu",
            languages=["python", "javascript"],
            tags=["fundamentals"],
            total_completed=100,
            total_attempted=120,
        )

        self.assertEqual(kata.name, "Multiply")
        self.assertEqual(kata.kata_id, "abc123")
        self.assertEqual(kata.languages, ["python", "javascript"])


class CodewarsServiceTests(TestCase):
    def test_save_kata_creates_new_kata(self):
        kata_data = {
            "id": "abc123",
            "name": "Multiply",
            "slug": "multiply",
            "url": "https://www.codewars.com/kata/abc123",
            "description": "Multiply two numbers.",
            "category": "reference",
            "rank": {
                "name": "8 kyu",
                "slug": "8-kyu",
            },
            "languages": ["python"],
            "tags": ["fundamentals"],
            "totalCompleted": 100,
            "totalAttempts": 120,
        }

        kata, created = save_kata(kata_data)

        self.assertTrue(created)
        self.assertEqual(kata.kata_id, "abc123")
        self.assertEqual(kata.name, "Multiply")
        self.assertEqual(kata.rank_name, "8 kyu")
        self.assertEqual(kata.languages, ["python"])

    def test_save_kata_updates_existing_kata(self):
        CodewarsKata.objects.create(
            kata_id="abc123",
            name="Old Name",
        )

        kata_data = {
            "id": "abc123",
            "name": "New Name",
            "slug": "new-name",
            "languages": ["python"],
            "tags": [],
            "rank": {
                "name": "7 kyu",
                "slug": "7-kyu",
            },
        }

        kata, created = save_kata(kata_data)

        self.assertFalse(created)
        self.assertEqual(kata.name, "New Name")
        self.assertEqual(kata.rank_name, "7 kyu")
        self.assertEqual(
            CodewarsKata.objects.count(),
            1,
        )

    @patch(
        "integrations.services.codewars._request_codewars"
    )
    def test_get_kata(self, mock_request):
        mock_request.return_value = {
            "id": "abc123",
            "name": "Multiply",
        }

        result = get_kata("abc123")

        mock_request.assert_called_once_with(
            "code-challenges/abc123"
        )

        self.assertEqual(
            result["id"],
            "abc123",
        )

    def test_get_kata_requires_identifier(self):
        with self.assertRaises(CodewarsAPIError):
            get_kata("")

    @patch(
        "integrations.services.codewars.get_kata"
    )
    def test_search_kata_caches_result(self, mock_get_kata):
        mock_get_kata.return_value = {
            "id": "abc123",
            "name": "Multiply",
            "slug": "multiply",
            "rank": {
                "name": "8 kyu",
                "slug": "8-kyu",
            },
            "languages": ["python"],
            "tags": [],
        }

        kata, created = search_kata("abc123")

        self.assertTrue(created)
        self.assertEqual(
            kata.kata_id,
            "abc123",
        )

        mock_get_kata.assert_called_once_with(
            "abc123"
        )