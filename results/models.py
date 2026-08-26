from django.conf import settings
from django.db import models


class Result(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RELEASED = "released"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RELEASED, "Released"),
    ]

    id = models.BigAutoField(primary_key=True)

    attempt = models.OneToOneField(
        "attempts.AssessmentAttempt",
        on_delete=models.CASCADE,
        related_name="result",
    )

    score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
    )

    total_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    released_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Result #{self.id} - Attempt #{self.attempt_id}"


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)

    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_feedback",
    )

    feedback_text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Feedback #{self.id} for Result #{self.result_id}"