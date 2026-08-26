from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Avg, Count, Max, Min

from .models import Result


def calculate_result(attempt):
    """
    Calculate the score, total possible points,
    and percentage for an assessment attempt.
    """

    answers = (
        attempt.answers
        .select_related("question")
        .all()
    )

    assessment = attempt.assessment

    questions = assessment.questions.all()

    total_points = sum(
        (
            question.points
            if question.points is not None
            else Decimal("0")
        )
        for question in questions
    )

    score = sum(
        (
            answer.points_awarded
            if answer.points_awarded is not None
            else Decimal("0")
        )
        for answer in answers
    )

    if total_points > 0:
        percentage = (
            Decimal(score)
            / Decimal(total_points)
            * Decimal("100")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    else:
        percentage = Decimal("0.00")

    return {
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
    }


@transaction.atomic
def create_result_for_attempt(attempt):
    """
    Create a result for an assessment attempt.

    A result is created only once per attempt.
    """

    result, created = Result.objects.get_or_create(
        attempt=attempt,
        defaults={
            "score": 0,
            "total_points": 0,
            "percentage": 0,
            "status": Result.STATUS_PENDING,
        },
    )

    if created:
        result_data = calculate_result(attempt)

        result.score = result_data["score"]
        result.total_points = result_data["total_points"]
        result.percentage = result_data["percentage"]

        result.save(
            update_fields=[
                "score",
                "total_points",
                "percentage",
                "updated_at",
            ]
        )

    return result


def refresh_result(attempt):
    """
    Recalculate an existing result after answers have been graded.
    """

    result = Result.objects.filter(
        attempt=attempt
    ).first()

    if not result:
        return create_result_for_attempt(attempt)

    result_data = calculate_result(attempt)

    result.score = result_data["score"]
    result.total_points = result_data["total_points"]
    result.percentage = result_data["percentage"]

    result.save(
        update_fields=[
            "score",
            "total_points",
            "percentage",
            "updated_at",
        ]
    )

    return result


def get_result_statistics():
    """
    Return aggregate statistics for released results.
    """

    released_results = Result.objects.filter(
        status=Result.STATUS_RELEASED
    )

    statistics = released_results.aggregate(
        total_results=Count("id"),
        average_percentage=Avg("percentage"),
        highest_percentage=Max("percentage"),
        lowest_percentage=Min("percentage"),
    )

    return {
        "total_results": statistics["total_results"] or 0,
        "average_percentage": (
            statistics["average_percentage"]
            or Decimal("0.00")
        ),
        "highest_percentage": (
            statistics["highest_percentage"]
            or Decimal("0.00")
        ),
        "lowest_percentage": (
            statistics["lowest_percentage"]
            or Decimal("0.00")
        ),
    }