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

    total_points = sum(
        (
            answer.question.points
            if answer.question.points is not None
            else Decimal("0")
        )
        for answer in answers
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

    existing_result = Result.objects.filter(
        attempt=attempt
    ).first()

    if existing_result:
        return existing_result

    result_data = calculate_result(attempt)

    return Result.objects.create(
        attempt=attempt,
        score=result_data["score"],
        total_points=result_data["total_points"],
        percentage=result_data["percentage"],
        status=Result.STATUS_PENDING,
    )


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
            statistics["average_percentage"] or 0
        ),
        "highest_percentage": (
            statistics["highest_percentage"] or 0
        ),
        "lowest_percentage": (
            statistics["lowest_percentage"] or 0
        ),
    }


def get_result_rankings():
    """
    Return released results ordered from highest
    percentage to lowest percentage.

    Results with the same percentage receive
    the same rank.
    """

    released_results = list(
        Result.objects
        .filter(status=Result.STATUS_RELEASED)
        .select_related("attempt")
        .order_by("-percentage", "id")
    )

    rankings = []

    previous_percentage = None
    current_rank = 0

    for position, result in enumerate(
        released_results,
        start=1,
    ):
        if result.percentage != previous_percentage:
            current_rank = position
            previous_percentage = result.percentage

        rankings.append(
            {
                "result": result,
                "rank": current_rank,
            }
        )

    return rankings