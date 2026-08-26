from django.conf import settings
from django.db import models


class Assessment(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    time_limit_minutes = models.PositiveIntegerField(default=60)

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessments"
    )

    invited_count = models.PositiveIntegerField(default=0)
    submitted_count = models.PositiveIntegerField(default=0)
    closes_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    TYPE_CHOICES = [
        ("mcq", "Multiple choice"),
        ("text", "Free text"),
        ("kata", "Coding kata"),
    ]
    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("codewars", "Codewars"),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="questions")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    prompt = models.TextField()
    order = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="manual")

    # Kata-specific — the "whiteboard" shape shared with Member 3 (submission)
    # and Member 4 (grading). Confirm before either builds against this.
    kata_bdd = models.TextField(null=True, blank=True)
    kata_pseudocode = models.TextField(null=True, blank=True)
    kata_difficulty = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.assessment.title} — {self.prompt[:40]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text
